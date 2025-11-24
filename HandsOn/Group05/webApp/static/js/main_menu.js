let estaciones = [];
let marcadores = [];
let controlRuta = null;
const origenInput = document.getElementById('origenInput');
const destinoInput = document.getElementById('destinoInput');
const origenDropdown = document.getElementById('origenDropdown');
const destinoDropdown = document.getElementById('destinoDropdown');


async function loadStations(useApi = true){
  if(useApi){
    let resource = await fetch('/api/allStations')
    estaciones = await resource.json();
  }else{
    estaciones = [];
    cleanMap()
  }

  // Change coords to Number
  estaciones.forEach(est => {
    est.coord = [ Number(est.coord[0]), Number(est.coord[1]) ];
  });
  paintMap(estaciones);

}


// --- Show initial pushpins with tooltip ---
async function paintMap(data) {

  
  for (const est of data) {
    // Espera a que llegue la respuesta del backend
    const response = await fetch("/api/stations/" + est.name);
    const extraData = await response.json();
    const binding = extraData.results.bindings[0]; 

    const address = binding?.address?.value || 'Dirección desconocida';
    const rawAddress = binding?.address?.value || 'Dirección desconocida';
    const cleanAddress = decodeURIComponent(rawAddress.split('/').pop());

    
    const capacity = binding?.capacity?.value || 'N/D';
    const photo = binding?.photo?.value || '';

    const info = `
      <strong>${est.name}</strong><br>
      📍 ${cleanAddress}<br>
      🚲 Capacidad: ${capacity}<br>
      <img src="${photo }" onerror="this.onerror=null; this.outerHTML='🖼️';" width="100">
    `;

    // Crea el marcador
    const marker = L.marker(est.coord, { icon: bikeIcon })
      .bindTooltip(info, { permanent: false, direction: 'top' })
      .addTo(map);

    // Click para asignar origen/destino
    marker.on('click', () => {
      try {
        const origenEl = document.getElementById('origenInput');
        const destinoEl = document.getElementById('destinoInput');

        if (origenEl && origenEl.value.trim() === '') {
          origenEl.value = est.name;
          origenEl.dispatchEvent(new Event('input'));
          origenEl.dispatchEvent(new Event('change'));
        } else if (destinoEl) {
          destinoEl.value = est.name;
          destinoEl.dispatchEvent(new Event('input'));
          destinoEl.dispatchEvent(new Event('change'));
        }
      } catch (err) {
        console.warn('Error cannot be assigned:', err);
      }
    });
  }
}

// --- Prepare the map ---
const map = L.map('map').setView([40.42, -3.69], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// --- Icon of where the bike is ---
const bikeIcon = L.icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/684/684908.png",
  iconSize: [28, 28],
  iconAnchor: [14, 28],
  popupAnchor: [0, -25]
});


function cleanMap(){
  marcadores.forEach(m => map.removeLayer(m));
  marcadores = [];
}

function normalize(s) {
  return String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
}

// searchStations: look by substring
function searchStations(q) {
  const qn = normalize(q).trim();
  if (!qn) return estaciones.slice(0, 10); // we see the first 10
  return estaciones.filter(e => normalize(e.name).includes(qn));
}

function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (m) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"}[m]));
}

function createItemHTML(est, q) {
  const qn = normalize(q).trim();
  const name = est.name;
  if (!qn) return `${escapeHtml(name)}`;
  const idx = normalize(name).indexOf(qn);
  if (idx === -1) return `${escapeHtml(name)}`;
  const before = name.slice(0, idx);
  const match = name.slice(idx, idx + qn.length);
  const after = name.slice(idx + qn.length);
  return `${escapeHtml(before)}<span class="match">${escapeHtml(match)}</span>${escapeHtml(after)}`;
}

function renderDropdown(dropdownEl, q) {
  const results = searchStations(q);
  dropdownEl.innerHTML = '';

  if (!results.length) {
    dropdownEl.innerHTML = `<div class="autocomplete-noresults">No results</div>`;
    dropdownEl.classList.remove('hidden');
    return;
  }

  const fragment = document.createDocumentFragment();
  results.forEach(r => {
    const wrapper = document.createElement('div');
    wrapper.className = 'autocomplete-item';
    wrapper.setAttribute('data-name', r.name);
    wrapper.innerHTML = createItemHTML(r, q);
    fragment.appendChild(wrapper);
  });

  dropdownEl.appendChild(fragment);
  dropdownEl.classList.remove('hidden');
  setActiveItem(dropdownEl, 0);
}

function setActiveItem(dropdownEl, index) {
  const items = Array.from(dropdownEl.querySelectorAll('.autocomplete-item'));
  items.forEach(it => it.classList.remove('active'));
  if (items.length === 0) return;
  const idx = Math.max(0, Math.min(index, items.length - 1));
  items[idx].classList.add('active');
  // scroll 
  const itemRect = items[idx].getBoundingClientRect();
  const listRect = dropdownEl.getBoundingClientRect();
  if (itemRect.top < listRect.top) items[idx].scrollIntoView({ block: 'nearest' });
  if (itemRect.bottom > listRect.bottom) items[idx].scrollIntoView({ block: 'nearest' });
}

function getActiveIndex(dropdownEl) {
  const items = Array.from(dropdownEl.querySelectorAll('.autocomplete-item'));
  return items.findIndex(it => it.classList.contains('active'));
}

function selectItem(inputEl, dropdownEl, name) {
  inputEl.value = name;
  dropdownEl.classList.add('hidden');
  inputEl.dispatchEvent(new Event('change'));
}

function attachAutocomplete(inputEl, dropdownEl) {
  let keyboardIndex = 0;

  inputEl.addEventListener('focus', (e) => {
    renderDropdown(dropdownEl, inputEl.value);
  });

  inputEl.addEventListener('input', (e) => {
    renderDropdown(dropdownEl, inputEl.value);
  });

  inputEl.addEventListener('keydown', (e) => {
    const items = Array.from(dropdownEl.querySelectorAll('.autocomplete-item'));
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      keyboardIndex = Math.min(items.length - 1, getActiveIndex(dropdownEl) + 1 || 0);
      setActiveItem(dropdownEl, keyboardIndex);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      keyboardIndex = Math.max(0, getActiveIndex(dropdownEl) - 1 || 0);
      setActiveItem(dropdownEl, keyboardIndex);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const active = dropdownEl.querySelector('.autocomplete-item.active');
      if (active) {
        selectItem(inputEl, dropdownEl, active.getAttribute('data-name'));
      }
    } else if (e.key === 'Escape') {
      dropdownEl.classList.add('hidden');
    }
  });

  dropdownEl.addEventListener('mousedown', (ev) => {
    const item = ev.target.closest('.autocomplete-item');
    if (!item) return;
    const name = item.getAttribute('data-name');
    selectItem(inputEl, dropdownEl, name);
  });

  document.addEventListener('click', (ev) => {
    if (!inputEl.contains(ev.target) && !dropdownEl.contains(ev.target)) {
      dropdownEl.classList.add('hidden');
    }
  });

  inputEl.addEventListener('blur', () => {
    setTimeout(() => dropdownEl.classList.add('hidden'), 150);
  });
}


attachAutocomplete(origenInput, origenDropdown);
attachAutocomplete(destinoInput, destinoDropdown);


function findCoordsByName(name) {
  if (!name) return null;
  const trimmed = name.trim().toLowerCase();
  const exact = estaciones.find(e => e.name.toLowerCase() === trimmed);
  if (exact) return exact.coord.slice();
  const starts = estaciones.find(e => e.name.toLowerCase().startsWith(trimmed));
  if (starts) return starts.coord.slice();
  return null;
}


document.getElementById('btnRuta').addEventListener('click', () => {
  const nameO = origenInput.value;
  const nameD = destinoInput.value;

  if (!nameO || !nameD) {
    alert("Select station of origin and destination");
    return;
  }

  const coordsO = findCoordsByName(nameO);
  const coordsD = findCoordsByName(nameD);

  if (!coordsO || !coordsD) {
    alert("No matching stations were found");
    return;
  }

  // Paint origin and destination
  cleanMap();
  paintMap([{'name': nameO, 'coord': coordsO}, {'name': nameD, 'coord': coordsD}]);

  
  const markerO = L.marker(coordsO, { icon: bikeIcon })
    .bindTooltip(nameO, { permanent: false, direction: 'top' })
    .addTo(map);
  marcadores.push(markerO);

  const markerD = L.marker(coordsD, { icon: bikeIcon })
    .bindTooltip(nameD, { permanent: false, direction: 'top' })
    .addTo(map);
  marcadores.push(markerD);

  const [latO, lonO] = coordsO;
  const [latD, lonD] = coordsD;

  // --- Routee in bike ---
  if (controlRuta) map.removeControl(controlRuta);
  controlRuta = L.Routing.control({
    waypoints: [
      L.latLng(latO, lonO),
      L.latLng(latD, lonD)
    ],
    router: L.Routing.osrmv1({
      serviceUrl: 'https://router.project-osrm.org/route/v1',
      profile: 'bike'
    }),
    lineOptions: {
      styles: [{ color: '#2e7d32', weight: 5, opacity: 0.9 }]
    },
    routeWhileDragging: false,
    show: false
  }).addTo(map);

  map.fitBounds(L.latLngBounds([[latO, lonO], [latD, lonD]]), { padding: [50, 50] });

  fetch(`/api/route_info/${encodeURIComponent(nameO)}/${encodeURIComponent(nameD)}`)
  .then(res => res.json())
  .then(data => {
    // Show trip information
    document.getElementById('routeInfo').classList.remove('hidden');
    document.getElementById('numTrips').textContent = data.num_travels || 0;
    document.getElementById('avgDuration').textContent = data.avg_duration.toFixed(2);
  })
  .catch(err => {
    console.error('Error fetching route info:', err);
    document.getElementById('routeInfo').classList.remove('hidden');
    document.getElementById('numTrips').textContent = 0;
    document.getElementById('avgDuration').textContent = 0;
  });
});


loadStations()