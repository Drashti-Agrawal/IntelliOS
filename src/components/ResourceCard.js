import React from 'react';

function ResourceCard() {
  return (
    <div className="card bg-dark text-white p-3 resource-card">
      <h5>Project X</h5>
      <div className="d-flex justify-content-between my-2">
        <button className="btn btn-outline-light btn-sm">Edit Resources</button>
        <button className="btn btn-primary btn-sm">Sync with dDNA</button>
      </div>
      <div className="mt-2">
        <div>CPU Usage <progress value="45" max="100" className="w-100" /></div>
        <div>Memory Usage <progress value="60" max="100" className="w-100" /></div>
        <div>Disk Usage <progress value="75" max="100" className="w-100" /></div>
        <div>Network Usage <progress value="30" max="100" className="w-100" /></div>
      </div>
    </div>
  );
}

export default ResourceCard;
