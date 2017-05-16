function radios() {
    student_form = document.getElementById("student-form")
    teacher_form = document.getElementById("teacher-form")
    coordinator_form = document.getElementById("coordinator-form")

    if (document.getElementById("student").checked == true) {
        student_form.style.cssText = "display: block;"
        teacher_form.style.cssText = "display: none;"
        coordinator_form.style.cssText = "display: none;"
    }
    else if (document.getElementById("teacher").checked == true) {
        student_form.style.cssText = "display: none;"
        teacher_form.style.cssText = "display: block;"
        coordinator_form.style.cssText = "display: none;"
    }
    else if (document.getElementById("coordinator").checked == true) {
        student_form.style.cssText = "display: none;"
        teacher_form.style.cssText = "display: none;"
        coordinator_form.style.cssText = "display: block;"
    }
}
