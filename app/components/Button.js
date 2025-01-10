import styles from './styles/button.module.css'
import Link from "next/link";

export function Button() {
  return (<div className={styles.container}>
    <div className={styles.start}>
    Show me the way
    <Link href="/search">
    <button
    type="button"
    className={styles.go}
    >
    Go
    </button>
    </Link>
    </div>

    </div>
  )
}