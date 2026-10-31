import sys
import termios
import tty

def main():
    fd = sys.stdin.fileno()
    # Save terminal state
    terminal_state = termios.tcgetattr(fd)

    print("Hold W/A/S/D. Press Q to quit.", flush=True)
    try:
        # Make the terminal not require pressing Enter for each input
        tty.setcbreak(fd)
        while True:
            key = sys.stdin.read(1).lower()

            if key == "q":
                break
            if key in "wasd":
                print(f"Pressed: {key}", flush=True)

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        sys.exit(0)

    # Restore terminal settings on Keyboard Interrput or crash
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, terminal_state)

if __name__ == "__main__":
    main()