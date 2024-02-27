function geoLocalization() {
    if (!navigator.geolocation) {
        console.warn('Geolocalização desativada')
        return
    }

    function success(position) {
        console.info('Geolocalização', position)
        const forms = document.getElementsByTagName('form')
        const localization = `${position.coords.latitude} , ${position.coords.longitude}`
        for (let i = 0; i < forms.length; i++) {
            const geoInput = document.createElement('input')
            geoInput.setAttribute('name', 'geo')
            geoInput.setAttribute('type', 'hidden')
            geoInput.setAttribute('value', localization)

            forms[i].appendChild(geoInput)
        }
    }
    function error() {
        console.error('Geolocalização falhou')
    }
    navigator.geolocation.getCurrentPosition(success, error)
}

function postLocalization() {
    if (!navigator.geolocation) return
    navigator.geolocation.getCurrentPosition((position) => {
        const body = JSON.stringify({ lat: position.coords.latitude, lon: position.coords.longitude })
        fetch('/api/location', {
            method: 'POST',
            mode: 'cors',
            cache: 'no-cache',
            headers: {
                "Content-Type": "application/json",
            },
            body: body
        }).then(response => console.info('Position sent - updated', response)).catch(err => console.error('Position not sent', err))
    }, (err) => {
        console.error('Geolocalização falhou', err)
    })
}

/** Aciona link para revisão da senha - template login.html */


// window.onload = postLocalization
