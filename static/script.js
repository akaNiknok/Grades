function radios() {
    // Radios
    student = document.getElementById("student")
    parent = document.getElementById("parent")
    teacher = document.getElementById("teacher")
    coordinator = document.getElementById("coordinator")

    // Forms
    student_form = document.getElementById("student-form")
    teacher_form = document.getElementById("teacher-form")
    coordinator_form = document.getElementById("coordinator-form")

    // Student Inputs
    student_grade = document.getElementById("student-grade")
    student_section = document.getElementById("student-section")
    student_cn = document.getElementById("student-cn")
    parent_username = document.getElementById("parent-username")
    parent_password = document.getElementById("parent-password")

    // Teacher and Coordinator Inputs
    teacher_pass = document.getElementById("teacher-pass")
    coordinator_pass = document.getElementById("coordinator-pass")

    // Student
    if (student.checked == true) {

        // Show student form
        student_form.style.cssText = "display: block;"
        teacher_form.style.cssText = "display: none;"
        coordinator_form.style.cssText = "display: none;"

        // Require Student
        student_grade.setAttribute("required", "required")
        student_section.setAttribute("required", "required")
        student_cn.setAttribute("required", "required")
        parent_username.setAttribute("required", "required")
        parent_password.setAttribute("required", "required")
        teacher_pass.removeAttribute("required")
        coordinator_pass.removeAttribute("required")
    }

    else if (parent.checked == true) {

        // Remove forms
        student_form.style.cssText = "display: none;"
        teacher_form.style.cssText = "display: none;"
        coordinator_form.style.cssText = "display: none;"

        // Remove required
        student_grade.removeAttribute("required")
        student_section.removeAttribute("required")
        student_cn.removeAttribute("required")
        parent_username.removeAttribute("required")
        parent_password.removeAttribute("required")
        teacher_pass.removeAttribute("required")
        coordinator_pass.removeAttribute("required")
    }

    // Teacher
    else if (teacher.checked == true) {

        // Show teacher form
        student_form.style.cssText = "display: none;"
        teacher_form.style.cssText = "display: block;"
        coordinator_form.style.cssText = "display: none;"

        // Require teacher
        student_grade.removeAttribute("required")
        student_section.removeAttribute("required")
        student_cn.removeAttribute("required")
        parent_username.removeAttribute("required")
        parent_password.removeAttribute("required")
        teacher_pass.setAttribute("required", "required")
        coordinator_pass.removeAttribute("required")
    }

    // coordinator
    else if (coordinator.checked == true) {

        // Show coordinator from
        student_form.style.cssText = "display: none;"
        teacher_form.style.cssText = "display: none;"
        coordinator_form.style.cssText = "display: block;"

        // Require coordinator
        student_grade.removeAttribute("required")
        student_section.removeAttribute("required")
        student_cn.removeAttribute("required")
        parent_username.removeAttribute("required")
        parent_password.removeAttribute("required")
        teacher_pass.removeAttribute("required")
        coordinator_pass.setAttribute("required", "required")
    }
}

// Initialize popovers
$(document).ready(function(){
    $('[data-toggle="popover"]').popover();
});

// https://www.abeautifulsite.net/whipping-file-inputs-into-shape-with-bootstrap-3
$(function() {

  // We can attach the `fileselect` event to all file inputs on the page
  $(document).on('change', ':file', function() {
    var input = $(this),
        numFiles = input.get(0).files ? input.get(0).files.length : 1,
        label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
    input.trigger('fileselect', [numFiles, label]);
  });

  // We can watch for our custom `fileselect` event like this
  $(document).ready( function() {
      $(':file').on('fileselect', function(event, numFiles, label) {

          var input = $(this).parents('.input-group').find(':text'),
              log = numFiles > 1 ? numFiles + ' files selected' : label;

          if( input.length ) {
              input.val(log);
          } else {
              if( log ) alert(log);
          }

      });
  });

});
