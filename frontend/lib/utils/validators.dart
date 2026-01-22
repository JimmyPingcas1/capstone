class Validators {
  // Email validation
  static String? email(String? value) {
    if (value == null || value.isEmpty) return "Email is required";
    final emailRegex = RegExp(r"^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$");
    if (!emailRegex.hasMatch(value)) return "Enter a valid email";
    return null;
  }

  // Password validation
  static String? password(String? value) {
    if (value == null || value.isEmpty) return "Password is required";
    if (value.length < 6) return "Password must be at least 6 characters";

    // Optional: require at least one letter and one number
    final passwordRegex = RegExp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$');
    if (!passwordRegex.hasMatch(value)) {
      return "Password must contain letters and numbers";
    }

    return null;
  }
}
