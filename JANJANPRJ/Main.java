package CCE105;
import java.util.Scanner;

public class Main {

	public static void main(String args[]) {
		Queue q = new Queue();
		 Scanner scanner = new Scanner(System.in);


		while (true) {
			System.out.println();
			System.out.println("=== AIRPORT BOARDING QUEUE ===");
            System.out.println("1. Check-in passenger");
            System.out.println("2. Board next passenger");
            System.out.println("3. View next passenger to board");
            System.out.println("4. Display queues and counts");
			System.out.println("5. End-of-day report and exit");
			System.out.print("Choose option: ");

			int choice;
			try {
				choice = Integer.parseInt(scanner.nextLine());
			} catch (NumberFormatException e) {
				System.out.println("Invalid input. Please enter a number 1-5.");
				continue;
			}

			switch (choice) {
				case 1:
					
					System.out.print("Enter passenger name: ");
					String name = scanner.nextLine();

					System.out.print("Enter priority (VIP/REGULAR): ");
					int type = scanner.nextInt();
					scanner.nextLine(); // Consume newline
					
					q.enqueue(name, type);
					break;
					
				case 2:
					q.Board();
					break;

				case 3:
					// next = q.Board();
					// System.out.println("Next passenger to board: " + next);
					break;

				case 4:
					q.display();
					break;

				case 5:
					System.out.println("End-of-day report written to 'end_of_day_report.txt'.");
					scanner.close();
					System.exit(0);

					break;
				default:
					System.out.println("Please choose a valid option (1-5).");
					break;
			}
		}

	}
}