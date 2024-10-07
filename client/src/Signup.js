import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Signup = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [messages, setMessages] = useState([]);
    const [error, setError] = useState('');  // Define error state
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        const response = await fetch('http://127.0.0.1:5000/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });
        const data = await response.json();
        if (data.success) {
            navigate('/login');
        } else {
            setError(data.message);  // Properly use setError to set the error message
        }
    };

    return (
        <div style={styles.container}>
            <div className="signup-container" style={styles.signupContainer}>
                <h1>Admin Sign-up</h1>
                {error && (  // Display error if there's one
                    <div style={styles.errorMessage}>{error}</div>
                )}
                {messages.length > 0 && (
                    <ul className="flash-messages" style={styles.flashMessages}>
                        {messages.map((message, index) => (
                            <li key={index} className="flash-message" style={styles.flashMessage}>
                                {message}
                            </li>
                        ))}
                    </ul>
                )}
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        name="username"
                        placeholder="Username"
                        required
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        style={styles.input}
                    />
                    <input
                        type="password"
                        name="password"
                        placeholder="Password"
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={styles.input}
                    />
                    <button type="submit" style={styles.button}>Sign Up</button>
                </form>
                <div className="login-link" style={styles.loginLink}>
                    Already have an account? <a href="/login">Log in</a>
                </div>
            </div>
        </div>
    );
};

const styles = {
    container: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        margin: '0',
        backgroundColor: '#f0f0f0',
    },
    signupContainer: {
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '5px',
        boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
    },
    input: {
        margin: '0.5rem 0',
        padding: '0.5rem',
        border: '1px solid #ddd',
        borderRadius: '3px',
    },
    button: {
        marginTop: '1rem',
        padding: '0.5rem',
        backgroundColor: '#007bff',
        color: 'white',
        border: 'none',
        borderRadius: '3px',
        cursor: 'pointer',
    },
    flashMessages: {
        listStyleType: 'none',
        padding: '0',
    },
    flashMessage: {
        backgroundColor: '#d4edda',
        borderColor: '#c3e6cb',
        color: '#155724',
        padding: '10px',
        marginBottom: '10px',
        borderRadius: '4px',
    },
    loginLink: {
        marginTop: '1rem',
        textAlign: 'center',
    },
    errorMessage: {
        color: 'red',
        marginBottom: '1rem',
    },
};

export default Signup;
