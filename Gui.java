import java.io.IOException;
import java.util.Scanner;

public class Main {

    public static void main(String[] args) {
        Queue queue = new Queue();
        Scanner scanner = new Scanner(System.in);

        boolean run = true;
        while (run) {
            System.out.println();
            System.out.println("=== AIRPORT BOARDING QUEUE ===");
            System.out.println("1. Check-in passenger");
            System.out.println("2. Board next passenger");
            System.out.println("3. View next passenger to board");
            System.out.println("4. Display queues and counts");
            System.out.println("5. Load manifest from CSV");
            System.out.println("6. Export boarding order to CSV");
            System.out.println("7. Exit");
            System.out.print("Choose option: ");

            int choice;
            try {
                choice = Integer.parseInt(scanner.nextLine());
            } catch (NumberFormatException e) {
                System.out.println("Invalid input. Please enter a number 1-7.");
                continue;
            }

            switch (choice) {
                case 1:
                    System.out.print("Enter passenger name: ");
                    String name = scanner.nextLine().trim();
                    if (name.isEmpty()) {
                        System.out.println("Name cannot be empty.");
                        break;
                    }
                    System.out.print("Enter group (PRIORITY/REGULAR): ");
                    String group = scanner.nextLine().trim();
                    if (group.isEmpty()) {
                        System.out.println("Group cannot be empty. Defaulting to REGULAR.");
                        group = "REGULAR";
                    }
                    queue.checkIn(name, group);
                    break;

                case 2:
                    queue.boardNext();
                    break;

                case 3:
                    Passenger next = queue.viewNext();
                    if (next == null) {
                        System.out.println("No passengers waiting to board.");
                    } else {
                        System.out.println("Next to board: " + next);
                    }
                    break;

                case 4:
                    queue.displayQueues();
                    break;

                case 5:
                    System.out.print("Enter CSV file path to load manifest: ");
                    String loadPath = scanner.nextLine().trim();
                    if (loadPath.isEmpty()) {
                        System.out.println("File path cannot be empty.");
                        break;
                    }
                    try {
                        queue.loadFromCsv(loadPath);
                    } catch (IOException e) {
                        System.out.println("Failed to load manifest: " + e.getMessage());
                    }
                    break;

                case 6:
                    System.out.print("Enter CSV file path to export boarding order: ");
                    String exportPath = scanner.nextLine().trim();
                    if (exportPath.isEmpty()) {
                        System.out.println("File path cannot be empty.");
                        break;
                    }
                    try {
                        queue.exportBoardingOrderToCsv(exportPath);
                    } catch (IOException e) {
                        System.out.println("Failed to export boarding order: " + e.getMessage());
                    }
                    break;

                case 7:
                    run = false;
                    System.out.println("Exiting. Goodbye.");
                    break;

                default:
                    System.out.println("Please choose a valid option (1-7).");
                    break;
            }
        }

        scanner.close();
    }
}
