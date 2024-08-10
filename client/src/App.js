// src/FileUpload.js
import React, { useState } from 'react';

const FileUpload = () => {
  const [fileName, setFileName] = useState('No file chosen');

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setFileName(file.name);
    }
  };

  const handleUpload = () => {
    const fileInput = document.querySelector('input[type="file"]');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    fetch('/upload', {
      method: 'POST',
      body: formData,
    })
      .then((response) => response.blob())
      .then((blob) => {
        const url = window.URL.createObjectURL(new Blob([blob]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'output.csv'); // Name of the downloaded file
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <h1>Upload HTML File to Convert to CSV</h1>
      <div style={{ margin: '20px' }}>
        <input type="file" onChange={handleFileChange} />
        <span style={{ marginLeft: '10px' }}>{fileName}</span>
        <button onClick={handleUpload} style={{ marginLeft: '10px' }}>Upload</button>
      </div>
    </div>
  );
};

export default FileUpload;
