package work01;

public class AgeCategory {

	public static void main(String[] args) {
		int age = 18;
		if (age < 18) {
			System.out.println("未成年");
		} else if (18 <= age && age < 65) {
			System.out.println("成人");
		} else {
			System.out.println("高齢者");
		}

	}

}
