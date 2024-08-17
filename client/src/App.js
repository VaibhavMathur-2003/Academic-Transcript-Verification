import React, { useState } from 'react';
import Papa from 'papaparse'; // Import PapaParse to handle CSV parsing
 
const FileUpload = () => {
  const [fileName, setFileName] = useState('No file chosen');
  const [tableData, setTableData] = useState([]);
 
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
      .then((response) => response.blob())  // Convert response to Blob
      .then((blob) => {
        // Automatically download the file
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'output.csv'); // Name of the downloaded file
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
 
        // Read the Blob and display its contents
        const reader = new FileReader();
        reader.onload = function(event) {
          const csvText = event.target.result;
          console.log(csvText);
          parseCSV(csvText);  // Parse the CSV text to JSON and display
        };
        reader.readAsText(blob); // Read the Blob as text
 
 
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  };
 
  const parseCSV = (csvText) => {
    Papa.parse(csvText, {
      header: true,  // Assumes the first row is the header
      dynamicTyping: true,  // Automatically convert numbers to their proper type
      complete: function(results) {
        setTableData(results.data);  // Set the parsed data to tableData state
      },
      error: function(error) {
        console.error('Error parsing CSV:', error);
      }
    });
  };
 
  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <h1>Upload File to Convert to CSV and Display Data</h1>
      <div style={{ margin: '20px' }}>
        <input type="file" onChange={handleFileChange} />
        <span style={{ marginLeft: '10px' }}>{fileName}</span>
        <button onClick={handleUpload} style={{ marginLeft: '10px' }}>Upload</button>
      </div>
 
      {tableData.length > 0 && (
        <div className="App" style={{ marginTop: '20px' }}>
          <h2>CSV Data</h2>
          <table border="1" cellPadding="5">
            <thead>
              <tr>
                <th>Course</th>
                <th>Course Title</th>
                <th>Credits</th>
                <th>Grade</th>
              </tr>
            </thead>
            <tbody>
              {tableData.map((val, key) => (
                <tr key={key}>
                  <td>{val.col1}</td>
                  <td>{val.col2}</td>
                  <td>{val.col3}</td>
                  <td>{val.Weighted}</td>
                  <td>{val.Average}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
 
export default FileUpload;