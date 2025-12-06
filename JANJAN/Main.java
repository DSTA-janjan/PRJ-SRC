package JANJAN;

import java.util.Scanner;

public class Main {

	public static void main(String args[]) {
		Queue q = new Queue();
		 Scanner scanner = new Scanner(System.in);

         q.load();
		while (true) {
			System.out.println();
			System.out.println("=== AIRPORT BOARDING QUEUE ===");
            System.out.println("1. Check-in passenger");
            System.out.println("2. Board next passenger");
            System.out.println("3. View next passenger to board");
            System.out.println("4. Display queues and counts");
			System.out.println("5. Terminate");
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
					int type;
					try {
						type = scanner.nextInt();
						scanner.nextLine();
					} catch (Exception e) {
						System.out.println("Invalid input. Please enter a valid number.");
						continue;
					}
					q.enqueue(name, type);
					break;
					
				case 2:
					q.Board();
					break;

				case 3:
                    if(q.countVIP() > 0)
                        System.out.println("Front passenger: " + q.peek(1, "front"));
					else
						 System.out.println("Front passenger: " + q.peek(2, "front"));
					break;

				case 4:
					q.display();
					break;

				case 5:
					System.out.println("Terminating the program, Thank you!.");
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