export const fadeIn = (direction, delay = 0, duration = 0.6) => {
    return {
      hidden: {
        y: direction === "up" ? 40 : direction === "down" ? -40 : 0,
        x: direction === "left" ? 40 : direction === "right" ? -40 : 0,
        opacity: 0,
      },
      show: {
        y: 0,
        x: 0,
        opacity: 1,
        transition: {
          type: "tween",
          duration,     // 👈 now dynamic
          delay,
          ease: [0.22, 1, 0.36, 1],
        },
      },
    };
  };
  