import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import FileUpload from "./FileUpload.js"; 
import AdminDashboard from "./AdminDashboard.js";
import Login from "./Login.js";
import Signup from "./Signup.js";
// import CourseReport from "./Report.js";
import "./App.css";

const App = () => {
    return (
        <Router>
            <div>
                <Routes>
                    <Route path="/" element={<FileUpload />} />
                    <Route path="/admin" element={<AdminDashboard />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/signup" element={<Signup />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;
