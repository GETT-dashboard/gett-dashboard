'use client';
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { TextField, Button, Typography, Paper, Box } from '@mui/material';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const router = useRouter();

    const handleLogin = async (e) => {
        e.preventDefault();

        // Call the API for login
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        const data = await res.json();
        console.log(data);
        if (res.status === 200) {
            // Assuming login is successful, you can store a flag/token in local storage
            router.push('/dashboard?successfulLogin=true');
        } else {
            setError(data.error || 'Login failed');
        }
    };

    return (
        <div className="flex justify-center items-center min-h-screen bg-gray-100">
            <Paper className="p-6 max-w-md w-full">
                <Typography variant="h4" align="center" gutterBottom>
                    Login
                </Typography>

                {error && <p className="text-red-500 text-center">{error}</p>}

                <form onSubmit={handleLogin} className="space-y-4">
                    <TextField
                        fullWidth
                        label="Username"
                        variant="outlined"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="mb-4"
                    />
                    <TextField
                        fullWidth
                        label="Password"
                        type="password"
                        variant="outlined"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="mb-4"
                    />

                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        color="primary"
                        className="mt-6"
                    >
                        Login
                    </Button>
                </form>
            </Paper>
        </div>
    );
};

export default Login;
