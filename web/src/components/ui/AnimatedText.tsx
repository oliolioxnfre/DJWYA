"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

/*
const genres = [
    "EDM",
    "Techno",
    "House",
    "Dubstep",
    "Trance",
    "Drum & Bass",
    "Hardstyle",
    "Electro",
    "Ambient",
    "Complextro",
    "Deep House",
    "Color Bass",
    "Riddim",
    "Brostep",
    "IDM",
    "Future Bass",
    "Hardcore",
    "Future House",

];
*/
const genres = [
    "Electronic", "EDM", "Techno", "House", "Dubstep", "Trance", "Electro",
    "Color Bass","Jungle", "Hardstyle", "Liquid DnB", "Deep House",
    "Psytrance", "Riddim", "Neurofunk", "Tech House", "Future Bass",
    "Breakbeat", "Acid Techno", "Bass House", "Jump Up", "Hard Techno",
    "Afro House", "Glitch Hop", "Frenchcore", "Vaporwave", "Garage", "Dub Techno",
    "G-House", "Wave", "2-Step", "Hard Dance", "Synthwave", "Darkstep", "Acid House",
    "Tech Trance", "Brostep", "Breakcore", "Funky House", "Nightcore", "IDM",
    "Techstep", "Dark Techno", "Color Bass", "Eurodance", "Complextro", "Big Room",
    "Chillstep", "Trip Hop", "Hyperpop", "Bass"
];

export function AnimatedText() {
    const [index, setIndex] = useState(0);

    useEffect(() => {
        const intervalId = setInterval(() => {
            setIndex((current) => (current + 1) % genres.length);
        }, 2500);
        return () => clearInterval(intervalId);
    }, []);

    return (
        <div className="flex flex-col items-center justify-center font-heading w-full">
            <div className="flex flex-col md:flex-row items-center gap-2 md:gap-4 text-5xl md:text-7xl lg:text-8xl font-black tracking-tighter w-full justify-center">
                <div className="relative h-[1.2em] w-[550px] sm:w-[450px] md:w-[600px] lg:w-[800px] overflow-hidden flex justify-end md:justify-end">
                    <AnimatePresence mode="popLayout">
                        <motion.span
                            key={genres[index]}
                            initial={{ y: 50, opacity: 0, filter: "blur(8px)" }}
                            animate={{ y: 0, opacity: 1, filter: "blur(0px)" }}
                            exit={{ y: -50, opacity: 0, filter: "blur(8px)" }}
                            transition={{
                                type: "spring",
                                stiffness: 300,
                                damping: 30,
                                mass: 1,
                            }}
                            className="absolute right-0 pr-2 md:pr-4 pb-4 whitespace-nowrap drop-shadow-[0_0_15px_rgba(255,0,255,0.5)]"
                            style={{
                                backgroundImage: 'linear-gradient(to right, #ff00ff, #ec4899, #8b5cf6)',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                color: 'transparent',
                            }}
                        >
                            {genres[index]}
                        </motion.span>
                    </AnimatePresence>
                </div>
                <span className="text-white pb-4 shrink-0 text-center md:text-left">
                    is for Everyone
                </span>
            </div>
        </div>
    );
}
