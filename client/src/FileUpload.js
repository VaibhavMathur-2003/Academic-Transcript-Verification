import React, { useState } from "react";
import Papa from "papaparse";
import "./App.css";

const FileUpload = () => {
  const [fileName, setFileName] = useState("No file chosen");
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
    formData.append("file", fileInput.files[0]);

    fetch("http://127.0.0.1:5000", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.blob())
      .then((blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", "output.csv");
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);

        const reader = new FileReader();
        reader.onload = function (event) {
          const csvText = event.target.result;
          console.log(csvText);
          parseCSV(csvText);
        };
        reader.readAsText(blob);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  const parseCSV = (csvText) => {
    Papa.parse(csvText, {
      header: true,
      dynamicTyping: true, 
      complete: function (results) {
        const filteredData = results.data.filter((row) => {
          const hasFInCredits = row.Grade === "F";
          const hasHSInCourse = row.Course && row.Course.includes("HS");
          return hasFInCredits || hasHSInCourse;
        });
        setTableData(filteredData);
      },
      error: function (error) {
        console.error("Error parsing CSV:", error);
      },
    });
  };

  return (
    <div className="file-upload-container">
      <h1>Upload File to Convert to CSV and Display Data</h1>
      <div className="file-upload">
        <input type="file" onChange={handleFileChange} id="fileInput" />
        <label htmlFor="fileInput" className="file-label">
          Choose File
        </label>
        <span className="file-name">{fileName}</span>
        <button onClick={handleUpload} className="upload-button">
          Upload
        </button>
      </div>

      {tableData.length > 0 && (
        <div className="table-container">
          <h2>CSV Data</h2>
          <table className="styled-table">
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
                  <td>{val.Course}</td>
                  <td>{val["Course Title"]}</td>
                  <td>{val.Credits}</td>
                  <td>{val.Grade}</td>
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
