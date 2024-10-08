import React, { useState } from 'react';

const AdminDashboard = () => {
    const [messages, setMessages] = useState([]);
    const [formData, setFormData] = useState({
        course: '',
        course_title: '',
        credits: '',
        reg_type: 'Regular',
        elective_type: 'Institute Core Theory'
    });
    const [csvFile, setCsvFile] = useState(null);

    // Handle form inputs for course fields
    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    // Handle file selection for CSV upload
    const handleFileChange = (e) => {
        setCsvFile(e.target.files[0]);
    };

    // Handle course form submission
    const handleSubmitCourse = async (e) => {
        e.preventDefault();
        const { course, course_title, credits, reg_type, elective_type } = formData;

        try {
            const response = await fetch('http://127.0.0.1:5000/admin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ course, course_title, credits, reg_type, elective_type }),
            });

            const data = await response.json();
            if (response.ok) {
                setMessages([...messages, 'Course added successfully!']);
                setFormData({
                    course: '',
                    course_title: '',
                    credits: '',
                    reg_type: 'Regular',
                    elective_type: 'Institute Core Theory',
                });
            } else {
                setMessages([...messages, 'Failed to add course: ' + data.error]);
            }
        } catch (error) {
            setMessages([...messages, 'Error: ' + error.message]);
        }
    };

    // Handle CSV form submission
    const handleSubmitCSV = async (e) => {
        e.preventDefault();
        if (!csvFile) {
            setMessages([...messages, 'Please select a CSV file']);
            return;
        }

        const formData = new FormData();
        formData.append('file', csvFile);

        try {
            const response = await fetch('http://127.0.0.1:5000/admin', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            if (response.ok) {
                setMessages([...messages, 'CSV uploaded successfully!']);
                setCsvFile(null);
            } else {
                setMessages([...messages, 'Failed to upload CSV: ' + data.error]);
            }
        } catch (error) {
            setMessages([...messages, 'Error: ' + error.message]);
        }
    };

    return (
        <div className="container" style={styles.container}>
            <h1>Admin Dashboard</h1>

            {messages.length > 0 && (
                <ul className="flash-messages" style={styles.flashMessages}>
                    {messages.map((message, index) => (
                        <li key={index} className="flash-message" style={styles.flashMessage}>
                            {message}
                        </li>
                    ))}
                </ul>
            )}

            <div className="section" style={styles.section}>
                <h2>Add Individual Course</h2>
                <form onSubmit={handleSubmitCourse} style={styles.form}>
                    <label htmlFor="course">Course:</label>
                    <input
                        type="text"
                        id="course"
                        name="course"
                        value={formData.course}
                        onChange={handleInputChange}
                        required
                        style={styles.input}
                    />

                    <label htmlFor="course_title">Course Title:</label>
                    <input
                        type="text"
                        id="course_title"
                        name="course_title"
                        value={formData.course_title}
                        onChange={handleInputChange}
                        required
                        style={styles.input}
                    />

                    <label htmlFor="credits">Credits:</label>
                    <input
                        type="number"
                        id="credits"
                        name="credits"
                        value={formData.credits}
                        onChange={handleInputChange}
                        required
                        style={styles.input}
                    />

                    <label htmlFor="reg_type">Registration Type:</label>
                    <select
                        id="reg_type"
                        name="reg_type"
                        value={formData.reg_type}
                        onChange={handleInputChange}
                        required
                        style={styles.select}
                    >
                        <option value="Regular">Regular</option>
                    </select>

                    <label htmlFor="elective_type">Elective Type:</label>
                    <select
                        id="elective_type"
                        name="elective_type"
                        value={formData.elective_type}
                        onChange={handleInputChange}
                        required
                        style={styles.select}
                    >
                        <option value="Institute Core Theory">Institute Core Theory</option>
                        <option value="Institute Core Theory + Lab">Institute Core Theory + Lab</option>
                        <option value="Institute Core Lab">Institute Core Lab</option>
                        <option value="Open Elective">Open Elective</option>
                        <option value="Program Elective">Program Elective</option>
                        <option value="Program Core Theory">Program Core Theory</option>
                        <option value="Program Core Theory + Lab">Program Core Theory + Lab</option>
                        <option value="Project">Project</option>
                    </select>

                    <button type="submit" style={styles.button}>Add Course</button>
                </form>
            </div>

            <div className="section" style={styles.section}>
                <h2>Upload CSV File</h2>
                <form onSubmit={handleSubmitCSV} encType="multipart/form-data" style={styles.form}>
                    <label htmlFor="file">Choose CSV file:</label>
                    <input
                        type="file"
                        id="file"
                        name="file"
                        accept=".csv"
                        onChange={handleFileChange}
                        required
                        style={styles.input}
                    />

                    <button type="submit" style={styles.button}>Upload CSV</button>
                </form>
            </div>
        </div>
    );
};

const styles = {
   
};

export default AdminDashboard;
