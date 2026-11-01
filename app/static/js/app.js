document.addEventListener('click', e => {
    const button = e.target.closest('[data-toggle]')
    if (!button) return
    const element = document.getElementById(button.dataset.toggle)
    if (element) element.classList.toggle('hidden')
})

document.querySelectorAll('[data-bg]').forEach(element => {
    const imageUrl = element.dataset.bg
    if (imageUrl) element.style.backgroundImage = `url("${imageUrl.replace(/"/g, '%22')}")`
})

document.querySelectorAll('.progress-fill').forEach(bar => {
    const value = Number(bar.dataset.progress) || 0
    const progress = Math.max(0, Math.min(100, value))
    bar.style.width = `${progress}%`
})

setTimeout(() => {
    document.querySelectorAll('.flash').forEach(element => element.classList.add('fade'))
}, 3500)
