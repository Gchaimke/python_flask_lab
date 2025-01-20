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
function get_gallery_div_image (image) {
  const galleryContainer = document.createElement('div')
  galleryContainer.classList.add('col-md-2')
  galleryContainer.setAttribute('data-aos', 'fade-up')

  const card = document.createElement('div')
  card.classList.add('card', 'mb-4', 'box-shadow')
  card.style.cursor = 'pointer'

  const img = document.createElement('img')
  img.classList.add('card-img-top')
  img.alt = 'name'
  img.src = '/static/img/public/' + image[1]
  img.setAttribute('data-path', image[1])
  img.setAttribute('data-holder-rendered', 'true')
  img.onclick = function () {
    setImage(image[1], 'gallery')
  }

  const p = document.createElement('p')
  p.classList.add('card-title')
  p.textContent = image[0]

  const i = document.createElement('i')
  i.classList.add('btn', 'bi', 'bi-trash', 'btn-danger')
  i.onclick = function () {
    deleteImage(image[1])
  }

  card.appendChild(img)
  card.appendChild(p)
  card.appendChild(i)
  galleryContainer.appendChild(card)

  return galleryContainer
}

function generatePageNumbers (totalPages) {
  const paginationContainer = document.getElementById('pagination')
  paginationContainer.innerHTML = ''

  for (let i = 1; i <= totalPages + 1; i++) {
    const pageItem = document.createElement('span')
    pageItem.classList.add('btn')
    pageItem.classList.add('btn-primary')
    pageItem.classList.add('col')
    pageItem.classList.add('mx-1')
    pageItem.classList.add('page-item')
    pageItem.href = '#'
    pageItem.textContent = i
    pageItem.addEventListener('click', function (e) {
      e.preventDefault()
      loadGalleryPage(i - 1)
      document
        .querySelectorAll('.page-item')
        .forEach(item => item.classList.remove('active'))
      pageItem.classList.add('active')
    })
    paginationContainer.appendChild(pageItem)
  }
}

function loadGalleryFromJson (url) {
  fetch(url)
    .then(response => response.json())
    .then(data => {
      const gallery = document.getElementById('gallery-body')
      gallery.innerHTML = ''
      data.images.forEach(image => {
        gallery.appendChild(get_gallery_div_image(image))
        generatePageNumbers(data.total_pages)
      })
    })
    .catch(error => {
      console.error('Error loading gallery:', error)
    })
}

function loadGalleryPage (page = 0) {
  const url = '/gallery?page=' + page
  loadGalleryFromJson(url)
}

function setImage (image_path, modal_id) {
  document.getElementById('picture_url').value = image_path
  document.getElementById('product_image').src =
    '/static/img/public/' + image_path
  modal_close(modal_id)
}

let get_from_url = document.querySelector('.get_from_url')
if (get_from_url) {
  get_from_url.addEventListener('click', function () {
    var image_name = document.getElementById('upload_image_name').value
    var image_url = this.parentElement.querySelector('.upload_image_url').value
    fetch('/gallery/upload_from_url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        image_url: image_url,
        image_name: image_name
      })
    })
      .then(response => response.text())
      .then(response => {
        if (!response.includes('Error')) {
          setImage(response, 'uploader')
        } else {
          alert(response)
        }
      })
      .catch(error => {
        console.error(error)
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
  upload_btn.addEventListener('click', function (e) {
    let formData = new FormData()
    formData.append('image', document.getElementById('imagefile').files[0])
    formData.append(
      'image_name',
      document.getElementById('upload_image_name').value
    )
    fetch('/gallery/upload_image', {
      method: 'POST',
      body: formData
    })
      .then(response => response.text())
      .then(response => {
        if (!response.includes('Error')) {
          setImage(response, 'uploader')
        } else {
          alert(response)
        }
      })
      .catch(error => {
        console.error(error)
      })
  })
}

function modal_close(modal_id) {
  let modal = bootstrap.Modal.getInstance(document.getElementById(modal_id))
  if (modal) {
    modal.hide()
  }
}

function deleteImage(image) {
  let confim = confirm('Delete this picture?')
  if (confim) {
    fetch('/gallery/delete_image', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        image: image
      })
    })
      .then(response => response.text())
      .then(data => {
        console.log(data)
        modal_close('gallery')
      })
      .catch(error => {
        console.error('Error:', error)
      })
    this.parentNode.parentNode.toggle()
  }
}
