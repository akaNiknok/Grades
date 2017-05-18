function radios() {
    student_form = document.getElementById("student-form")
    teacher_form = document.getElementById("teacher-form")
    coordinator_form = document.getElementById("coordinator-form")

    // Student Inputs
    student_grade = document.getElementById("student-grade")
    student_section = document.getElementById("student-section")
    student_cn = document.getElementById("student-cn")

    // Teacher and Coordinator Inputs
    teacher_pass = document.getElementById("teacher-pass")
    coordinator_pass = document.getElementById("coordinator-pass")

    // Student
    if (document.getElementById("student").checked == true) {

        // Show student form
        student_form.style.cssText = "display: block;"
        teacher_form.style.cssText = "display: none;"
        coordinator_form.style.cssText = "display: none;"

        // Require Student
        student_grade.setAttribute("required", "required")
        student_section.setAttribute("required", "required")
        student_cn.setAttribute("required", "required")
        teacher_pass.removeAttribute("required")
        coordinator_pass.removeAttribute("required")
    }

    // Teacher
    else if (document.getElementById("teacher").checked == true) {

        // Show teacher form
        student_form.style.cssText = "display: none;"
        teacher_form.style.cssText = "display: block;"
        coordinator_form.style.cssText = "display: none;"

        // Require teacher
        student_grade.removeAttribute("required")
        student_section.removeAttribute("required")
        student_cn.removeAttribute("required")
        teacher_pass.setAttribute("required", "required")
        coordinator_pass.removeAttribute("required")
    }

    // coordinator
    else if (document.getElementById("coordinator").checked == true) {

        // Show coordinator from
        student_form.style.cssText = "display: none;"
        teacher_form.style.cssText = "display: none;"
        coordinator_form.style.cssText = "display: block;"

        // Require coordinator
        student_grade.removeAttribute("required")
        student_section.removeAttribute("required")
        student_cn.removeAttribute("required")
        teacher_pass.removeAttribute("required")
        coordinator_pass.setAttribute("required", "required")
    }
}
