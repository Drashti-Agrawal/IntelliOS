// src/components/PermissionCheckboxes.js
import React, { useState } from 'react';

const permissionsList = [
  'Allow System Monitoring',
  'Enable File Access',
  'Grant Network Access',
  'Log System Events'
];

const PermissionCheckboxes = () => {
  const [permissions, setPermissions] = useState({});

  const togglePermission = (perm) => {
    setPermissions(prev => ({ ...prev, [perm]: !prev[perm] }));
  };

  return (
    <div className="permissions-container">
      {permissionsList.map(perm => (
        <label key={perm}>
          <input
            type="checkbox"
            checked={permissions[perm] || false}
            onChange={() => togglePermission(perm)}
          />
          {perm}
        </label>
      ))}
    </div>
  );
};

export default PermissionCheckboxes;
