"use client";

import React from "react";
import { motion } from "framer-motion";

interface SonicDNA {
    intensity: number;
    euphoria: number;
    space: number;
    pulse: number;
    chaos: number;
    swing: number;
    bass: number;
}

interface StarChartProps {
    dna: SonicDNA | null;
    size?: number;
}

export const StarChart: React.FC<StarChartProps> = ({ dna, size = 500 }) => {
    const categories = ["INTENSITY", "EUPHORIA", "SPACE", "PULSE", "CHAOS", "SWING", "BASS"];
    const catKeys: (keyof SonicDNA)[] = ["intensity", "euphoria", "space", "pulse", "chaos", "swing", "bass"];

    const currentDna = dna || {
        intensity: 0, euphoria: 0, space: 0, pulse: 0, chaos: 0, swing: 0, bass: 0,
    };

    const rawValues = catKeys.map((key) => currentDna[key] || 0);
    const maxVal = Math.max(...rawValues, 1);
    const scaler = 10 / maxVal;
    const scaledValues = rawValues.map((v) => Math.round((v * scaler) / 2) * 2);

    const centerX = size / 2;
    const centerY = size / 2;
    // Reduce radius slightly to leave room for labels
    const radius = size * 0.35; 
    const valleyR = radius * 0.356; 

    const getX = (angleDeg: number, r: number) => {
        const angleRad = (angleDeg - 90) * (Math.PI / 180);
        return centerX + r * Math.cos(angleRad);
    };

    const getY = (angleDeg: number, r: number) => {
        const angleRad = (angleDeg - 90) * (Math.PI / 180);
        return centerY + r * Math.sin(angleRad);
    };

    // 1. Diamonds for each category
    const diamonds = catKeys.map((key, i) => {
        const peakVal = (scaledValues[i] / 10) * radius;
        const angle = i * (360 / 7);
        const lAngle = angle - (360 / 14);
        const rAngle = angle + (360 / 14);

        // Center Point is actually slightly offset to create depth
        const centerOffset = radius * 0.133;
        
        const points = [
            `${getX(angle, centerOffset)},${getY(angle, centerOffset)}`,
            `${getX(lAngle, valleyR)},${getY(lAngle, valleyR)}`,
            `${getX(angle, peakVal)},${getY(angle, peakVal)}`,
            `${getX(rAngle, valleyR)},${getY(rAngle, valleyR)}`,
        ].join(" ");

        const hue = i * (360 / 7);
        return {
            points,
            fill: `hsla(${hue}, 80%, 55%, 0.55)`,
            stroke: `hsla(${hue}, 80%, 55%, 0.9)`,
            label: categories[i]
        };
    });

    // 2. Heptagrams for background
    const outerAngles = Array.from({ length: 8 }, (_, i) => i * (360 / 7));
    const acuteAngles = Array.from({ length: 8 }, (_, i) => (i * 3 * 360) / 7);
    const obtuseAngles = Array.from({ length: 8 }, (_, i) => (i * 2 * 360) / 7);
    const invertedAngles = Array.from({ length: 8 }, (_, i) => (i * 3 * 360) / 7 + 360 / 14);

    const getHexPath = (angles: number[], r: number) => {
        return angles.map((a, i) => `${i === 0 ? "M" : "L"} ${getX(a, r)},${getY(a, r)}`).join(" ") + " Z";
    };

    const colorGrey = "rgba(155, 155, 155, 0.4)";

    return (
        <div className="relative w-full h-full flex items-center justify-center">
            <svg width="100%" height="100%" viewBox={`0 0 ${size} ${size}`} className="overflow-visible">
                {/* Background Heptagrams */}
                <path d={getHexPath(outerAngles, radius)} fill="none" stroke={colorGrey} strokeWidth="5" />
                <path d={getHexPath(acuteAngles, radius)} fill="none" stroke={colorGrey} strokeWidth="2.8" />
                <path d={getHexPath(obtuseAngles, radius)} fill="none" stroke={colorGrey} strokeWidth="1" />
                <path d={getHexPath(invertedAngles, valleyR)} fill="rgba(150, 150, 150, 0.1)" stroke={colorGrey} strokeWidth="1.5" />

                {/* Radial Dots */}
                {Array.from({ length: 7 }).map((_, i) => {
                    const angle = i * (360 / 7);
                    return [2, 4, 6, 8, 10].map((r) => (
                        <circle
                            key={`dot-${i}-${r}`}
                            cx={getX(angle, (r / 10) * radius)}
                            cy={getY(angle, (r / 10) * radius)}
                            r="2"
                            fill="rgba(255, 255, 255, 0.4)"
                        />
                    ));
                })}

                {/* Diamonds (The Data) */}
                {diamonds.map((dia, i) => (
                    <motion.polygon
                        key={`dia-${i}`}
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: i * 0.1, duration: 0.5 }}
                        points={dia.points}
                        fill={dia.fill}
                        stroke={dia.stroke}
                        strokeWidth="1.5"
                    />
                ))}

                {/* Category Labels */}
                {categories.map((cat, i) => {
                    const angle = i * (360 / 7);
                    const labelR = radius + 30;
                    return (
                        <text
                            key={`label-${i}`}
                            x={getX(angle, labelR)}
                            y={getY(angle, labelR)}
                            fill="white"
                            fontSize="10"
                            fontWeight="bold"
                            textAnchor="middle"
                            dominantBaseline="middle"
                            className="bg-black/50"
                        >
                            {cat}
                        </text>
                    );
                })}
            </svg>
        </div>
    );
};
