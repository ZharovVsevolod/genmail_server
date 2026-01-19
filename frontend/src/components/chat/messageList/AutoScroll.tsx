import { useRef } from "react";

export const useAutoScroll = <T extends HTMLElement>() => {
  const ref = useRef<T | null>(null);

  const scroll = () => ref.current?.scrollIntoView({ behavior: "smooth" });

  return { ref, scroll };
};
