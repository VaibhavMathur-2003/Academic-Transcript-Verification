import React, { useState } from 'react';

function UploadForm() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [reportData, setReportData] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!selectedFile) {
      alert('Please select a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://localhost:5000/', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const report = await response.json(); // Assuming the Flask API returns JSON data
        setReportData(report);
      } else {
        alert('File upload failed. Please try again.');
      }
    } catch (error) {
      console.error('Error uploading the file:', error);
      alert('An error occurred while uploading the file.');
    }
  };

  return (
    <div>
      <h2>Upload HTML File</h2>
      <form onSubmit={handleSubmit} encType="multipart/form-data">
        <input type="file" name="file" onChange={handleFileChange} />
        <button type="submit">Upload</button>
      </form>

      {/* Render report data */}
      {reportData && (
        <div>
          <h2>Report</h2>

          {/* Elective Credits Section */}
          <section>
            <h3>Elective Credits</h3>
            <table>
              <thead>
                <tr>
                  <th>Elective Type</th>
                  <th>Total Credits</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(reportData.elective_credits).map(([elective, credits]) => (
                  <tr key={elective}>
                    <td>{elective}</td>
                    <td>{credits}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          {/* Missing Courses Section */}
          {reportData.missing_courses && (
            <section>
              <h3>Missing Courses</h3>
              <table>
                <thead>
                  <tr>
                    <th>Course Code</th>
                    <th>Course Title</th>
                    <th>Elective Type</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(reportData.missing_courses).map(([courseCode, courseInfo]) => (
                    <tr key={courseCode}>
                      <td>{courseCode}</td>
                      <td>{courseInfo.title}</td>
                      <td>{courseInfo.elective_type}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          )}

          {/* CPI Section */}
          <section>
            <h3>CPI for Each Semester</h3>
            <table>
              <thead>
                <tr>
                  <th>CPI</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(reportData.section_averages).map(([semester, cpi]) => (
                  <tr key={cpi}>
                    <td>{cpi}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
          {console.log(reportData)}

          {/* All Courses Section */}
          <section>
            <h3>All Courses</h3>
            <table>
              <thead>
                <tr>
                  <th>Course Code</th>
                  <th>Course Title</th>
                  <th>Credits</th>
                  <th>Reg. Type</th>
                  <th>Elective Type</th>
                  <th>Grade</th>
                </tr>
              </thead>
              <tbody>
                {reportData.courses.map((course, index) => (
                  <tr key={index}>
                    <td>{course[0]}</td>
                    <td>{course[1]}</td>
                    <td>{course[2]}</td>
                    <td>{course[3]}</td>
                    <td>{course[4]}</td>
                    <td>{course[5]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </div>
      )}
    </div>
  );
}

export default UploadForm;
