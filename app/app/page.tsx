import Image from "next/image";
import { Button } from "../components/Button"
import styles from "../components/styles/bg.module.css"

export default function Home() {
  return (
    <div className={styles.background}>
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start">
        <title> Heatmap </title>
        
        <div className="flex gap-4 items-center flex-col sm:flex-row">
          <Button/>
        </div>

      </main>
      <footer className="row-start-3 mt-10 flex gap-6 flex-wrap items-center justify-center">
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://git.pg.edu.pl/p1348918/heatmapa-trojmiasto"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="https://nextjs.org/icons/globe.svg"
            alt="Globe icon"
            width={16}
            height={16}
          />
          See source code →
        </a>
      </footer>
    </div>
  );
}
