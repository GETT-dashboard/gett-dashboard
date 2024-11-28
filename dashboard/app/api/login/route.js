import { NextResponse } from 'next/server';
// import { db } from '@/lib/db'; // Assuming your database connection is in db.js
import connection from '../../lib/db.js';
import jwt from 'jsonwebtoken';
import { serialize } from 'cookie';
import 'server-only';

const SECRET_KEY = process.env.SECRET_KEY || 'your-very-secure-secret-key';

export async function POST(request) {

    return NextResponse.json({ error: 'No session token found' }, { status: 401 });
    // const { username, password } = await request.json();

    // try {
    //     // Fetch the user from the database
    //     const query = `SELECT * FROM User WHERE username = ? and passwordHash = SHA2(CONCAT(salt, ?), 256);`;
    //     console.log(query);

    //     const [rows, fields] = await connection.promise().execute(query, [username, password])
    //     console.log(rows);

    //     if (!rows.length) {
    //         console.log('User not found');
    //         return NextResponse.json({ error: 'Invalid credentials' }, { status: 401 });
    //     }

    //     const dbUser = rows[0];

    //     // Generate a session token (e.g., JWT)
    //     const sessionToken = jwt.sign(
    //         { username: dbUser.username, userId: dbUser.id },
    //         SECRET_KEY,
    //         { expiresIn: '1h' } // Token expiration
    //     );

    //     // Set the session token in a secure HTTP-only cookie
    //     const cookie = serialize('session_token', sessionToken, {
    //         httpOnly: true, // Prevent client-side JavaScript from accessing the cookie
    //         secure: process.env.NODE_ENV === 'production', // Use secure cookies in production
    //         sameSite: 'strict', // Protect against CSRF attacks
    //         path: '/', // Make the cookie available across the entire site
    //         maxAge: 7200, // 1 hour expiration,
    //     });

    //     const response = NextResponse.json({ message: 'Login successful', username: dbUser.username }, { status: 200 });
    //     response.headers.set('Set-Cookie', cookie);

    //     return response;
    // } catch (error) {
    //     return NextResponse.json({ error: 'Something went wrong' }, { status: 500 });
    // }
}

export async function GET(request) {
    const sessionToken = request.cookies.get('session_token');

    if (!sessionToken) {
        return NextResponse.json({ error: 'No session token found' }, { status: 401 });
    }

    try {
        const decoded = jwt.verify(sessionToken, SECRET_KEY);
        return NextResponse.json({ message: 'Session is active', user: decoded }, { status: 200 });
    } catch (error) {
        return NextResponse.json({ error: 'Invalid session token' }, { status: 401 });
    }
}
