import React from 'react'
import { Link } from 'react-router-dom'

export default function Logo() {
    return (
        <Link to="/" className="sagarr-logo-full">
            <svg className="sagarr-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none">
                <circle
                    className="ring"
                    cx="50"
                    cy="50"
                    r="42"
                    strokeWidth="6"
                    strokeLinecap="round"
                    strokeDasharray="50 16"
                    transform="rotate(-20 50 50)"
                />
                <g className="compass" transform="translate(50,50) rotate(-45)">
                    <line y1="-24" y2="24" strokeWidth="4" strokeLinecap="round" />
                    <circle cy="-24" r="7" />
                    <circle r="8" />
                    <circle cy="24" r="7" />
                </g>
            </svg>

            <span className="sagarr-wordmark">Sagarr</span>
        </Link>
    )
}
