import React from 'react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        const response = await fetch('http://127.0.0.1:5000/login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
          });
          const data = await response.json();
          if (data.success) {
            navigate('/admin'); 
          } else {
            setError(data.message); 
          }
    };

    return (
        <div style={styles.container}>
            <div className="login-container" style={styles.loginContainer}>
                <h1>Admin Login</h1>
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
                    <button type="submit" style={styles.button}>Login</button>
                    {error && <div style={styles.error}>{error}</div>}
                </form>
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
    loginContainer: {
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
    error: {
        color: 'red',
        marginTop: '0.5rem',
        textAlign: 'center',
    },
};

export default Login;
