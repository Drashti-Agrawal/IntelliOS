"""
State Synchronization Agent - Manages dDNA state persistence and synchronization.

This agent is responsible for:
- Persisting dDNA state to storage systems
- Synchronizing state across devices
- Managing state versioning and conflict resolution
- Handling state backup and recovery
- Coordinating with external storage services
"""

import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import hashlib

from .base_agent import BaseAgent
from core.ddna_state import DigitalDNAState, update_state_timestamp


@dataclass
class StateVersion:
    """Version information for dDNA state."""
    version_id: str
    timestamp: datetime
    hash: str
    size: int
    description: str
    is_synced: bool = False


@dataclass
class SyncStatus:
    """Synchronization status information."""
    last_sync: Optional[datetime] = None
    sync_interval: int = 300  # seconds
    is_syncing: bool = False
    sync_errors: List[str] = None
    pending_changes: int = 0


class StateSyncAgent(BaseAgent):
    """
    State Synchronization Agent - Manages dDNA state persistence and sync.
    
    Responsibilities:
    - Persist dDNA state to local and remote storage
    - Synchronize state across multiple devices
    - Handle state versioning and conflict resolution
    - Manage state backup and recovery
    - Coordinate with external storage services (Firebase, etc.)
    """
    
    def __init__(self, name: str = "StateSyncAgent"):
        super().__init__(name, "Manages dDNA state persistence and synchronization")
        self.state_dir = Path(".intellios/state")
        self.backup_dir = Path(".intellios/backups")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_version: Optional[StateVersion] = None
        self.version_history: List[StateVersion] = []
        self.sync_status = SyncStatus()
        self.max_versions = 50
        self.auto_backup_interval = 3600  # 1 hour
        
        # Initialize Firebase client (if configured)
        self.firebase_client = None
        self._init_firebase()
        
    def _init_firebase(self) -> None:
        """Initialize Firebase client if credentials are available."""
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            # Check for Firebase credentials
            cred_path = Path("firebase-credentials.json")
            if cred_path.exists():
                cred = credentials.Certificate(str(cred_path))
                firebase_admin.initialize_app(cred)
                self.firebase_client = firestore.client()
                self.logger.info("Firebase client initialized")
            else:
                self.logger.info("Firebase credentials not found, using local storage only")
                
        except ImportError:
            self.logger.info("Firebase SDK not installed, using local storage only")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Firebase: {e}")
            
    def _calculate_state_hash(self, state: DigitalDNAState) -> str:
        """
        Calculate a hash of the dDNA state for versioning.
        
        Args:
            state: dDNA state to hash
            
        Returns:
            SHA-256 hash of the state
        """
        # Convert state to JSON string and hash it
        state_json = json.dumps(state, default=str, sort_keys=True)
        return hashlib.sha256(state_json.encode()).hexdigest()
        
    def _create_state_version(self, state: DigitalDNAState, description: str = "") -> StateVersion:
        """
        Create a new state version.
        
        Args:
            state: Current dDNA state
            description: Description of the version
            
        Returns:
            New state version
        """
        state_hash = self._calculate_state_hash(state)
        state_json = json.dumps(state, default=str, sort_keys=True)
        
        version = StateVersion(
            version_id=f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            hash=state_hash,
            size=len(state_json),
            description=description or f"State update at {datetime.now().isoformat()}"
        )
        
        return version
        
    def _save_state_locally(self, state: DigitalDNAState, version: StateVersion) -> bool:
        """
        Save state to local storage.
        
        Args:
            state: dDNA state to save
            version: State version information
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Save current state
            current_state_file = self.state_dir / "current_state.json"
            with open(current_state_file, 'w') as f:
                json.dump(state, f, default=str, indent=2)
                
            # Save versioned state
            version_file = self.state_dir / f"{version.version_id}.json"
            with open(version_file, 'w') as f:
                json.dump(state, f, default=str, indent=2)
                
            # Save version metadata
            version_meta_file = self.state_dir / f"{version.version_id}.meta.json"
            with open(version_meta_file, 'w') as f:
                json.dump(asdict(version), f, default=str, indent=2)
                
            self.logger.info(f"State saved locally: {version.version_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save state locally: {e}")
            return False
            
    def _load_state_locally(self, version_id: str = None) -> Optional[DigitalDNAState]:
        """
        Load state from local storage.
        
        Args:
            version_id: Specific version to load, None for current
            
        Returns:
            Loaded dDNA state or None if failed
        """
        try:
            if version_id:
                state_file = self.state_dir / f"{version_id}.json"
            else:
                state_file = self.state_dir / "current_state.json"
                
            if not state_file.exists():
                return None
                
            with open(state_file, 'r') as f:
                state_data = json.load(f)
                
            # Convert string timestamps back to datetime objects
            for key, value in state_data.items():
                if isinstance(value, dict) and 'timestamp' in value:
                    try:
                        value['timestamp'] = datetime.fromisoformat(value['timestamp'])
                    except (ValueError, TypeError):
                        pass
                        
            return state_data
            
        except Exception as e:
            self.logger.error(f"Failed to load state locally: {e}")
            return None
            
    async def _sync_to_firebase(self, state: DigitalDNAState, version: StateVersion) -> bool:
        """
        Synchronize state to Firebase (if available).
        
        Args:
            state: dDNA state to sync
            version: State version information
            
        Returns:
            True if sync was successful, False otherwise
        """
        if not self.firebase_client:
            return False
            
        try:
            # Get Firestore collection
            collection = self.firebase_client.collection('intellios_states')
            
            # Prepare state data for Firestore
            state_data = {
                'version_id': version.version_id,
                'timestamp': version.timestamp,
                'hash': version.hash,
                'size': version.size,
                'description': version.description,
                'state': state,
                'synced_at': datetime.now()
            }
            
            # Save to Firestore
            doc_ref = collection.document(version.version_id)
            doc_ref.set(state_data)
            
            self.logger.info(f"State synced to Firebase: {version.version_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync to Firebase: {e}")
            return False
            
    async def _load_from_firebase(self, version_id: str = None) -> Optional[DigitalDNAState]:
        """
        Load state from Firebase (if available).
        
        Args:
            version_id: Specific version to load, None for latest
            
        Returns:
            Loaded dDNA state or None if failed
        """
        if not self.firebase_client:
            return None
            
        try:
            collection = self.firebase_client.collection('intellios_states')
            
            if version_id:
                # Load specific version
                doc_ref = collection.document(version_id)
                doc = doc_ref.get()
                if doc.exists:
                    return doc.to_dict()['state']
            else:
                # Load latest version
                docs = collection.order_by('timestamp', direction='DESCENDING').limit(1).stream()
                for doc in docs:
                    return doc.to_dict()['state']
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to load from Firebase: {e}")
            return None
            
    def _cleanup_old_versions(self) -> None:
        """Remove old state versions to prevent storage bloat."""
        try:
            # Get all version files
            version_files = list(self.state_dir.glob("*.json"))
            meta_files = list(self.state_dir.glob("*.meta.json"))
            
            # Keep only the most recent versions
            if len(version_files) > self.max_versions:
                # Sort by modification time
                version_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                # Remove old files
                for old_file in version_files[self.max_versions:]:
                    old_file.unlink()
                    
                    # Remove corresponding meta file
                    meta_file = old_file.with_suffix('.meta.json')
                    if meta_file.exists():
                        meta_file.unlink()
                        
                self.logger.info(f"Cleaned up {len(version_files) - self.max_versions} old versions")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old versions: {e}")
            
    def _create_backup(self, state: DigitalDNAState) -> bool:
        """
        Create a backup of the current state.
        
        Args:
            state: dDNA state to backup
            
        Returns:
            True if backup was successful, False otherwise
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_dir / f"backup_{timestamp}.json"
            
            with open(backup_file, 'w') as f:
                json.dump(state, f, default=str, indent=2)
                
            self.logger.info(f"Backup created: {backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return False
            
    async def process(self, state: DigitalDNAState) -> DigitalDNAState:
        """
        Main processing method - manages state persistence and synchronization.
        
        Args:
            state: Current dDNA state
            
        Returns:
            Updated dDNA state
        """
        self.logger.info("Starting state synchronization")
        
        # Update state timestamp
        state = update_state_timestamp(state)
        
        # Create new version
        version = self._create_state_version(state, "Regular state update")
        
        # Save locally
        local_success = self._save_state_locally(state, version)
        
        # Sync to Firebase (if available)
        firebase_success = await self._sync_to_firebase(state, version)
        
        # Update version tracking
        if local_success:
            self.current_version = version
            self.version_history.append(version)
            version.is_synced = firebase_success
            
        # Update sync status
        self.sync_status.last_sync = datetime.now()
        self.sync_status.is_syncing = False
        if not firebase_success and self.firebase_client:
            self.sync_status.sync_errors = [f"Firebase sync failed for {version.version_id}"]
            
        # Cleanup old versions
        self._cleanup_old_versions()
        
        # Create backup if needed
        if self._should_create_backup():
            self._create_backup(state)
            
        # Add agent message
        from core.ddna_state import add_agent_message
        sync_message = f"State synchronized: {version.version_id}"
        if firebase_success:
            sync_message += " (local + Firebase)"
        else:
            sync_message += " (local only)"
            
        state = add_agent_message(state, self.agent_name, sync_message, "state_sync")
        
        self.logger.info("State synchronization completed")
        return state
        
    def _should_create_backup(self) -> bool:
        """Check if a backup should be created based on time interval."""
        if not self.sync_status.last_sync:
            return True
            
        time_since_backup = datetime.now() - self.sync_status.last_sync
        return time_since_backup.total_seconds() > self.auto_backup_interval
        
    def get_state_version(self, version_id: str) -> Optional[DigitalDNAState]:
        """
        Get a specific version of the state.
        
        Args:
            version_id: Version ID to retrieve
            
        Returns:
            State at the specified version or None if not found
        """
        # Try local storage first
        state = self._load_state_locally(version_id)
        if state:
            return state
            
        # Try Firebase if available
        if self.firebase_client:
            # This would need to be async, but we'll handle it synchronously for now
            return None
            
        return None
        
    def get_version_history(self) -> List[StateVersion]:
        """
        Get the history of state versions.
        
        Returns:
            List of state versions
        """
        return self.version_history.copy()
        
    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get current synchronization status.
        
        Returns:
            Dictionary containing sync status information
        """
        return {
            "last_sync": self.sync_status.last_sync.isoformat() if self.sync_status.last_sync else None,
            "sync_interval": self.sync_status.sync_interval,
            "is_syncing": self.sync_status.is_syncing,
            "sync_errors": self.sync_status.sync_errors or [],
            "pending_changes": self.sync_status.pending_changes,
            "firebase_available": self.firebase_client is not None,
            "current_version": self.current_version.version_id if self.current_version else None,
            "total_versions": len(self.version_history)
        }
        
    async def force_sync(self, state: DigitalDNAState) -> bool:
        """
        Force a synchronization of the current state.
        
        Args:
            state: Current dDNA state to sync
            
        Returns:
            True if sync was successful, False otherwise
        """
        self.logger.info("Forcing state synchronization")
        
        version = self._create_state_version(state, "Forced sync")
        
        # Save locally
        local_success = self._save_state_locally(state, version)
        
        # Sync to Firebase
        firebase_success = await self._sync_to_firebase(state, version)
        
        if local_success:
            self.current_version = version
            self.version_history.append(version)
            version.is_synced = firebase_success
            
        self.sync_status.last_sync = datetime.now()
        
        return local_success and firebase_success
        
    def restore_from_backup(self, backup_file: str) -> Optional[DigitalDNAState]:
        """
        Restore state from a backup file.
        
        Args:
            backup_file: Path to the backup file
            
        Returns:
            Restored state or None if failed
        """
        try:
            backup_path = self.backup_dir / backup_file
            if not backup_path.exists():
                self.logger.error(f"Backup file not found: {backup_file}")
                return None
                
            with open(backup_path, 'r') as f:
                state_data = json.load(f)
                
            self.logger.info(f"State restored from backup: {backup_file}")
            return state_data
            
        except Exception as e:
            self.logger.error(f"Failed to restore from backup: {e}")
            return None
            
    def list_backups(self) -> List[str]:
        """
        List available backup files.
        
        Returns:
            List of backup file names
        """
        backup_files = list(self.backup_dir.glob("backup_*.json"))
        return [f.name for f in sorted(backup_files, key=lambda x: x.stat().st_mtime, reverse=True)]
