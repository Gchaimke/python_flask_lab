;(function () {
  'use strict'

  /**
   * Apply .scrolled class to the body as the page is scrolled down
   */
  function toggleScrolled () {
    const selectBody = document.querySelector('body')
    const selectHeader = document.querySelector('#header')
    if (selectHeader == null) return
    if (
      !selectHeader.classList.contains('scroll-up-sticky') &&
      !selectHeader.classList.contains('sticky-top') &&
      !selectHeader.classList.contains('fixed-top')
    )
      return
    window.scrollY > 100
      ? selectBody.classList.add('scrolled')
      : selectBody.classList.remove('scrolled')
  }

  document.addEventListener('scroll', toggleScrolled)
  window.addEventListener('load', toggleScrolled)

  /**
   * Mobile nav toggle
   */
  const mobileNavToggleBtn = document.querySelector('.mobile-nav-toggle')

  function mobileNavToogle () {
    document.querySelector('body').classList.toggle('mobile-nav-active')
    mobileNavToggleBtn.classList.toggle('bi-list')
    mobileNavToggleBtn.classList.toggle('bi-x')
  }
  if (mobileNavToggleBtn) {
    mobileNavToggleBtn.addEventListener('click', mobileNavToogle)
  }

  /**
   * Hide mobile nav on same-page/hash links
   */
  document.querySelectorAll('#navmenu a').forEach(navmenu => {
    navmenu.addEventListener('click', () => {
      if (document.querySelector('.mobile-nav-active')) {
        mobileNavToogle()
      }
    })
  })

  /**
   * Toggle mobile nav dropdowns
   */
  document.querySelectorAll('.navmenu .toggle-dropdown').forEach(navmenu => {
    navmenu.addEventListener('click', function (e) {
      e.preventDefault()
      this.parentNode.classList.toggle('active')
      this.parentNode.nextElementSibling.classList.toggle('dropdown-active')
      e.stopImmediatePropagation()
    })
  })

  /**
   * Preloader
   */
  const preloader = document.querySelector('#preloader')
  if (preloader) {
    window.addEventListener('load', () => {
      preloader.remove()
    })
  }

  /**
   * Scroll top button
   */
  let scrollTop = document.querySelector('.scroll-top')

  function toggleScrollTop () {
    if (scrollTop) {
      window.scrollY > 100
        ? scrollTop.classList.add('active')
        : scrollTop.classList.remove('active')
    }
  }
  if (scrollTop) {
    scrollTop.addEventListener('click', e => {
      e.preventDefault()
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      })
    })
  }

  window.addEventListener('load', toggleScrollTop)
  document.addEventListener('scroll', toggleScrollTop)

  /**
   * Animation on scroll function and init
   */
  function aosInit () {
    if (typeof AOS === 'undefined') return
    AOS.init({
      duration: 600,
      easing: 'ease-in-out',
      once: true,
      mirror: false
    })
  }
  window.addEventListener('load', aosInit)

  /**
   * Correct scrolling position upon page load for URLs containing hash links.
   */
  window.addEventListener('load', function (e) {
    if (window.location.hash) {
      if (document.querySelector(window.location.hash)) {
        setTimeout(() => {
          let section = document.querySelector(window.location.hash)
          let scrollMarginTop = getComputedStyle(section).scrollMarginTop
          window.scrollTo({
            top: section.offsetTop - parseInt(scrollMarginTop),
            behavior: 'smooth'
          })
        }, 100)
      }
    }
  })

  /**
   * Navmenu Scrollspy
   */
  let navmenulinks = document.querySelectorAll('.navmenu a')

  function navmenuScrollspy () {
    navmenulinks.forEach(navmenulink => {
      if (!navmenulink.hash) return
      let section = document.querySelector(navmenulink.hash)
      if (!section) return
      let position = window.scrollY + 200
      if (
        position >= section.offsetTop &&
        position <= section.offsetTop + section.offsetHeight
      ) {
        document
          .querySelectorAll('.navmenu a.active')
          .forEach(link => link.classList.remove('active'))
        navmenulink.classList.add('active')
      } else {
        navmenulink.classList.remove('active')
      }
    })
  }
  window.addEventListener('load', navmenuScrollspy)
  document.addEventListener('scroll', navmenuScrollspy)

  var btn_delete = document.querySelector('#delete_message')
  if (btn_delete) {
    btn_delete.addEventListener('click', function (e) {
      if (confirm("Are you sure? deleted data can't be recovered!") == true) {
        document.querySelector('#form_delete').submit()
      } else {
        e.preventDefault()
      }
    })
  }
})()

/**
 * Open page with "ctrl+alt+l"
 */
document.addEventListener('keydown', function (e) {
  if (e.ctrlKey && e.altKey && e.key === 'l') {
    window.location.href = '/lab'
  }
})
document.addEventListener('keydown', function (e) {
  if (e.ctrlKey && e.altKey && e.key === 'p') {
    window.location.href = '/products/power_supplies'
  }
})

//Gallery & Uploader
function setImage(image_path) {
  document.getElementById('picture_url').value = image_path
  document.getElementById('product_image').src = '/static/img/public/'+image_path
  modal_close('gallery')
}

function deleteImage(image_path) {
  let confim = confirm('Delete this picture?')
  if (confim) {
    fetch('/gallery/delete_image', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        image: image_path
      })
    })
      .then(response => response.text())
      .then(data => {
        alert(data)
      })
      .catch(error => {
        console.error('Error:', error)
      })
    this.parentNode.parentNode.toggle()
  }
}

let get_from_url = document.querySelector('.get_from_url')
if (get_from_url) {
  get_from_url.addEventListener('click', function () {
    var name = document.getElementById('upload_image_name').value
    var url = this.parentElement.querySelector('.upload_image_url').value
    fetch('/gallery/upload_from_url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        url: url,
        name: name
      })
    })
      .then(response => response.text())
      .then(response => {
        document.getElementById('picture_url').value = 'products/' + response
        alert(response + ' uploaded!')
        modal_close('uploader')
      })
      .catch(error => {
        console.error('Error:', error)
      })
  })
}

let upload_image = document.querySelector('.upload_image')
if (upload_image) {
  upload_image.forEach(toggle => {
    toggle.addEventListener('click', function () {
      document.getElementById('upload_image_name').value =
        this.getAttribute('data-name')
    })
  })
}

let upload_btn = document.querySelector('.upload_btn')
if (upload_btn) {
  upload_btn.addEventListener('click', function () {
    var files = document.getElementById('imagefile').files
    console.log(files)
    var name = document.getElementById('upload_image_name').value
    if (files.length > 0 && name != '') {
      fetch('/gallery/upload_image', {
        method: 'POST',
        body: new URLSearchParams({
          file: files[0],
          name: name
        })
      })
        .then(response => response.text())
        .then(response => {
          if (response != 'Error') {
            alert(response)
            document.getElementById('picture_url').value =
              'products/' + response
            modal_close('uploader')
          } else {
            alert('file not uploaded')
          }
        })
        .catch(error => {
          console.error('Error:', error)
        })
    } else {
      alert('Please select a file and set name!')
    }
  })
}

function modal_close (modal_id) {
  let modal = bootstrap.Modal.getInstance(document.getElementById(modal_id))
  modal.hide()
}
