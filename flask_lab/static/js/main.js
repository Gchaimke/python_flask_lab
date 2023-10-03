var btn_delete = document.querySelector('#delete_message')

if (btn_delete) {
   btn_delete.addEventListener('click', function (e) {
    if (confirm("Are you sure, deleted post can't be recovered?") == true) {
      document.querySelector('#form_delete').submit()
    } else {
      e.preventDefault()
    }
  })
}
