"""
Workspace Configuration Agent - Manages workspace setup and environment configuration.

This agent is responsible for:
- Detecting and configuring workspace environments
- Managing project-specific settings
- Handling workspace state persistence
- Coordinating with development tools and IDEs
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from .base_agent import BaseAgent
from core.ddna_state import DigitalDNAState, WorkspaceContext


class WorkspaceConfigAgent(BaseAgent):
    """
    Workspace Configuration Agent - Manages workspace environments and settings.
    
    Responsibilities:
    - Detect workspace type and configuration
    - Manage project-specific settings and dependencies
    - Handle workspace state persistence
    - Coordinate with development tools and IDEs
    - Monitor workspace changes and updates
    """
    
    def __init__(self, name: str = "WorkspaceConfigAgent"):
        super().__init__(name, "Manages workspace setup and environment configuration")
        self.workspace_root = Path.cwd()
        self.config_file = self.workspace_root / ".intellios" / "workspace.json"
        self.supported_workspace_types = [
            "python", "javascript", "typescript", "java", "csharp", 
            "go", "rust", "php", "ruby", "general"
        ]
        
    def _detect_workspace_type(self) -> str:
        """
        Detect the type of workspace based on project files.
        
        Returns:
            Workspace type string
        """
        # Check for common project files
        if (self.workspace_root / "requirements.txt").exists():
            return "python"
        elif (self.workspace_root / "package.json").exists():
            return "javascript"
        elif (self.workspace_root / "tsconfig.json").exists():
            return "typescript"
        elif (self.workspace_root / "pom.xml").exists():
            return "java"
        elif (self.workspace_root / "*.csproj").exists():
            return "csharp"
        elif (self.workspace_root / "go.mod").exists():
            return "go"
        elif (self.workspace_root / "Cargo.toml").exists():
            return "rust"
        elif (self.workspace_root / "composer.json").exists():
            return "php"
        elif (self.workspace_root / "Gemfile").exists():
            return "ruby"
        else:
            return "general"
            
    def _scan_project_structure(self) -> Dict[str, Any]:
        """
        Scan the project structure to understand the codebase.
        
        Returns:
            Dictionary containing project structure information
        """
        structure = {
            "files": [],
            "directories": [],
            "file_types": {},
            "total_files": 0,
            "total_directories": 0
        }
        
        # Common directories to ignore
        ignore_dirs = {
            ".git", ".vscode", ".idea", "__pycache__", "node_modules",
            ".pytest_cache", ".mypy_cache", "build", "dist", "target"
        }
        
        for root, dirs, files in os.walk(self.workspace_root):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            # Count files and directories
            structure["total_directories"] += len(dirs)
            structure["total_files"] += len(files)
            
            # Track file types
            for file in files:
                ext = Path(file).suffix.lower()
                structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
                
        return structure
        
    def _detect_dependencies(self) -> Dict[str, List[str]]:
        """
        Detect project dependencies based on workspace type.
        
        Returns:
            Dictionary containing dependency information
        """
        dependencies = {
            "runtime": [],
            "development": [],
            "build": [],
            "tools": []
        }
        
        workspace_type = self._detect_workspace_type()
        
        if workspace_type == "python":
            # Check for requirements.txt
            req_file = self.workspace_root / "requirements.txt"
            if req_file.exists():
                with open(req_file, 'r') as f:
                    dependencies["runtime"] = [
                        line.strip() for line in f.readlines()
                        if line.strip() and not line.startswith('#')
                    ]
                    
            # Check for setup.py or pyproject.toml
            if (self.workspace_root / "setup.py").exists():
                dependencies["build"].append("setuptools")
            if (self.workspace_root / "pyproject.toml").exists():
                dependencies["build"].append("poetry")
                
        elif workspace_type == "javascript":
            # Check for package.json
            pkg_file = self.workspace_root / "package.json"
            if pkg_file.exists():
                try:
                    with open(pkg_file, 'r') as f:
                        pkg_data = json.load(f)
                        dependencies["runtime"] = list(pkg_data.get("dependencies", {}).keys())
                        dependencies["development"] = list(pkg_data.get("devDependencies", {}).keys())
                except json.JSONDecodeError:
                    self.logger.warning("Could not parse package.json")
                    
        return dependencies
        
    def _detect_ide_config(self) -> Dict[str, Any]:
        """
        Detect IDE and editor configuration.
        
        Returns:
            Dictionary containing IDE configuration information
        """
        ide_config = {
            "detected_ides": [],
            "config_files": [],
            "extensions": []
        }
        
        # Check for common IDE config directories
        ide_dirs = {
            ".vscode": "VS Code",
            ".idea": "IntelliJ IDEA",
            ".vs": "Visual Studio",
            ".sublime-project": "Sublime Text"
        }
        
        for dir_name, ide_name in ide_dirs.items():
            if (self.workspace_root / dir_name).exists():
                ide_config["detected_ides"].append(ide_name)
                ide_config["config_files"].append(dir_name)
                
        return ide_config
        
    def _load_workspace_config(self) -> Dict[str, Any]:
        """
        Load existing workspace configuration.
        
        Returns:
            Dictionary containing workspace configuration
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(f"Could not load workspace config: {e}")
                
        return {}
        
    def _save_workspace_config(self, config: Dict[str, Any]) -> None:
        """
        Save workspace configuration to file.
        
        Args:
            config: Configuration dictionary to save
        """
        # Ensure .intellios directory exists
        config_dir = self.config_file.parent
        config_dir.mkdir(exist_ok=True)
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.logger.info(f"Workspace config saved to {self.config_file}")
        except IOError as e:
            self.logger.error(f"Could not save workspace config: {e}")
            
    async def process(self, state: DigitalDNAState) -> DigitalDNAState:
        """
        Main processing method - analyzes and configures workspace.
        
        Args:
            state: Current dDNA state
            
        Returns:
            Updated dDNA state with workspace information
        """
        self.logger.info("Starting workspace configuration analysis")
        
        # Detect workspace type
        workspace_type = self._detect_workspace_type()
        self.logger.info(f"Detected workspace type: {workspace_type}")
        
        # Scan project structure
        project_structure = self._scan_project_structure()
        self.logger.info(f"Project structure: {project_structure['total_files']} files, {project_structure['total_directories']} directories")
        
        # Detect dependencies
        dependencies = self._detect_dependencies()
        
        # Detect IDE configuration
        ide_config = self._detect_ide_config()
        
        # Create workspace context
        workspace_context = WorkspaceContext(
            workspace_type=workspace_type,
            workspace_path=str(self.workspace_root),
            project_structure=project_structure,
            dependencies=dependencies,
            ide_configuration=ide_config,
            last_updated=datetime.now()
        )
        
        # Update state with workspace information
        state.workspace_context = workspace_context
        
        # Save configuration
        config = {
            "workspace_type": workspace_type,
            "project_structure": project_structure,
            "dependencies": dependencies,
            "ide_config": ide_config,
            "last_updated": datetime.now().isoformat()
        }
        self._save_workspace_config(config)
        
        # Add agent message
        from core.ddna_state import add_agent_message
        state = add_agent_message(
            state,
            self.agent_name,
            f"Workspace configured: {workspace_type} project with {project_structure['total_files']} files",
            "workspace_config"
        )
        
        self.logger.info("Workspace configuration analysis completed")
        return state
        
    def get_workspace_info(self) -> Dict[str, Any]:
        """
        Get current workspace information.
        
        Returns:
            Dictionary containing workspace information
        """
        return {
            "workspace_type": self._detect_workspace_type(),
            "workspace_path": str(self.workspace_root),
            "config_file": str(self.config_file),
            "config_exists": self.config_file.exists()
        }
        
    def update_workspace_config(self, updates: Dict[str, Any]) -> None:
        """
        Update workspace configuration with new settings.
        
        Args:
            updates: Dictionary containing configuration updates
        """
        current_config = self._load_workspace_config()
        current_config.update(updates)
        current_config["last_updated"] = datetime.now().isoformat()
        
        self._save_workspace_config(current_config)
        self.logger.info("Workspace configuration updated")
        
    def get_supported_workspace_types(self) -> List[str]:
        """
        Get list of supported workspace types.
        
        Returns:
            List of supported workspace type strings
        """
        return self.supported_workspace_types.copy()
