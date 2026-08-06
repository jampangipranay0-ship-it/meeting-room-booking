document.addEventListener('DOMContentLoaded', function () {
  const clock = document.getElementById('live-clock');
  if (clock) {
    const updateClock = () => {
      const now = new Date();
      clock.textContent = now.toLocaleTimeString('en-IN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
        timeZone: 'Asia/Kolkata'
      });
    };
    updateClock();
    setInterval(updateClock, 1000);
  }

  const purpose = document.getElementById('purpose');
  const meetingLink = document.getElementById('meeting_link');
  const clientNameLabel = document.getElementById('client_name_label');
  const clientNameInput = document.getElementById('client_name_input');
  const meetingLinkRow = meetingLink ? meetingLink.parentElement : null;
  const startTimeSelect = document.getElementById('start_time');
  const endTimeSelect = document.getElementById('end_time');
  const isAdmin = document.body.dataset.userRole === 'admin';
  const TIME_SLOTS = ['09:00','09:30','10:00','10:30','11:00','11:30','12:00','12:30','13:00','13:30','14:00','14:30','15:00','15:30','16:00','16:30','17:00','17:30','18:00','18:30','19:00','19:30','20:00','20:30'];
  // not using Choices.js for time selects; will populate native selects directly

  const toMinutes = (time) => {
    const [h, m] = time.split(':').map(Number);
    return h * 60 + m;
  };

  const toTime = (minutes) => {
    const hour = String(Math.floor(minutes / 60)).padStart(2, '0');
    const min = String(minutes % 60).padStart(2, '0');
    return `${hour}:${min}`;
  };

  const getBlockedSlots = (bookings) => {
    const blocked = new Set();
    bookings.forEach((booking) => {
      const start = toMinutes(booking.start_time);
      const end = toMinutes(booking.end_time);
      for (let time = start; time < end; time += 30) {
        blocked.add(toTime(time));
      }
    });
    return blocked;
  };

  // Replace Choices.js-enhanced dropdowns with native select population
  const START_SLOTS = TIME_SLOTS.slice(0, TIME_SLOTS.length - 1);
  const END_SLOTS = TIME_SLOTS.slice(1);

  const populateSelect = (selectEl, slots, blocked) => {
    if (!selectEl) return;
    const prevValue = selectEl.value;
    // clear existing options
    selectEl.innerHTML = '';
    slots.forEach((slot) => {
      const opt = document.createElement('option');
      opt.value = slot;
      if (blocked.has(slot)) {
        opt.text = `${slot} 🔴 Booked`;
        opt.disabled = true;
        opt.className = 'booked-option';
      } else {
        opt.text = slot;
      }
      selectEl.appendChild(opt);
    });
    try { selectEl.disabled = false; } catch (e) { /* ignore */ }
    // restore previous selection if still valid, else pick first available
    if (prevValue && !blocked.has(prevValue) && Array.from(selectEl.options).some(o => o.value === prevValue)) {
      selectEl.value = prevValue;
    } else {
      const firstAvailable = Array.from(selectEl.options).find(o => !o.disabled);
      if (firstAvailable) selectEl.value = firstAvailable.value;
    }
  };

  const updateDropdowns = (blocked) => {
    populateSelect(startTimeSelect, START_SLOTS, blocked);
    populateSelect(endTimeSelect, END_SLOTS, blocked);
  };

  const updateClientLabel = (purposeValue) => {
    if (!clientNameLabel) return;

    if (purposeValue === 'Client Meeting' || purposeValue === 'Sales Call') {
      clientNameLabel.textContent = 'Client Name';
      clientNameInput.placeholder = 'Enter client name';
    } else if (purposeValue === 'Candidate Interview' || purposeValue === 'Interview Panel') {
      clientNameLabel.textContent = 'Candidate Name';
      clientNameInput.placeholder = 'Enter candidate name';
    } else if (purposeValue === 'HR Discussion' || purposeValue === 'One-on-One') {
      clientNameLabel.textContent = 'Person Name';
      clientNameInput.placeholder = 'Enter person name';
    } else {
      clientNameLabel.textContent = 'Client / Candidate Name';
      clientNameInput.placeholder = 'Enter client or candidate name';
    }
  };

  if (purpose) {
    updateClientLabel(purpose.value);
    purpose.addEventListener('change', function () {
      updateClientLabel(this.value);
      if (this.value === 'Online Meeting') {
        meetingLinkRow?.classList.remove('d-none');
      } else {
        if (meetingLink) meetingLink.value = '';
        meetingLinkRow?.classList.add('d-none');
      }
    });
  }

  const bookingDate = document.getElementById('booking_date');
  const room_id = document.getElementById('room_id');
  const bookedSlotsList = document.getElementById('booked_slots_list');
  const welcomeScreen = document.getElementById('welcome-screen');
  const appShell = document.getElementById('app-shell');
  const welcomeAccept = document.getElementById('welcome-accept');
  const welcomeExit = document.getElementById('welcome-exit');
  const welcomeAnimation = document.getElementById('robotAnimation');
  const heroAnimation = document.getElementById('heroAnimation');
  const isRootPage = window.location.pathname === '/' || window.location.pathname === '';
  const skipWelcomeAttr = welcomeScreen?.dataset.skipWelcome === 'true';
  const hasSeenWelcome = sessionStorage.getItem('welcomeSeen') === 'true';

  const fetchBookedSlots = async () => {
    if (!bookingDate || !room_id || !bookedSlotsList) return;

    const roomId = room_id.value;
    const date = bookingDate.value;
    if (!roomId || !date) return;

    bookedSlotsList.innerHTML = '<li class="list-group-item">Loading availability...</li>';

    try {
      const response = await fetch(`/room_availability?room_id=${encodeURIComponent(roomId)}&date=${encodeURIComponent(date)}`);
      const bookings = await response.json();
      if (!Array.isArray(bookings) || bookings.length === 0) {
        bookedSlotsList.innerHTML = '<li class="list-group-item">No bookings for selected room and date.</li>';
      updateDropdowns(getBlockedSlots([]));
      return;
    }

    const blockedSlots = getBlockedSlots(bookings);
    updateDropdowns(blockedSlots);

    bookedSlotsList.innerHTML = bookings.map(booking => {
        const state = booking.status === 'Booked' ? 'Booked' : booking.status === 'Pending Approval' ? 'Blocked' : booking.status;
        if (isAdmin) {
          const nameText = booking.client_name ? ` - ${booking.client_name}` : '';
          const purposeText = booking.purpose ? ` (${booking.purpose})` : '';
          return `<li class="list-group-item"><strong>${booking.start_time}</strong> - <strong>${booking.end_time}</strong>${nameText}${purposeText} <span class="badge bg-secondary ms-2">${state}</span></li>`;
        }
        return `<li class="list-group-item"><strong>${booking.start_time}</strong> - <strong>${booking.end_time}</strong> - ${state}</li>`;
      }).join('');
    } catch (error) {
      bookedSlotsList.innerHTML = '<li class="list-group-item text-danger">Unable to load availability.</li>';
    }
  };

  if (bookingDate) {
    const today = new Date();
    const todayString = today.toISOString().split('T')[0];
    const maxDate = new Date(today);
    maxDate.setDate(maxDate.getDate() + 7);
    const maxDateString = maxDate.toISOString().split('T')[0];

    bookingDate.setAttribute('min', todayString);
    bookingDate.setAttribute('max', maxDateString);
    bookingDate.value = todayString;
    bookingDate.addEventListener('change', () => {
      if (bookingDate.value < todayString || bookingDate.value > maxDateString) {
        bookingDate.value = todayString;
      }
      fetchBookedSlots();
    });
  }

  if (room_id) {
    room_id.addEventListener('change', fetchBookedSlots);
  }

  if (bookingDate && room_id) {
    fetchBookedSlots();
  }

  if (startTimeSelect || endTimeSelect) {
    updateDropdowns(new Set());
  }

  const showApp = () => {
    if (welcomeScreen) {
      welcomeScreen.classList.add('is-hidden');
      setTimeout(() => {
        welcomeScreen.style.display = 'none';
      }, 450);
    }
    if (appShell) {
      appShell.classList.remove('blurred');
    }
    sessionStorage.setItem('welcomeSeen', 'true');
  };

  const showWelcome = () => {
    if (welcomeScreen) {
      welcomeScreen.style.display = 'flex';
      welcomeScreen.classList.remove('is-hidden');
    }
    if (appShell) {
      appShell.classList.add('blurred');
    }
  };

  if (welcomeAnimation) {
    if (window.lottie) {
      try {
        const animationPath = (window.STATIC_URL || '/static/') + 'animations/robot-hi.json';
        window.lottie.loadAnimation({
          container: welcomeAnimation,
          renderer: 'svg',
          loop: true,
          autoplay: true,
          path: animationPath,
        });
      } catch (error) {
        console.error('Welcome Lottie loadAnimation failed', error);
      }
    } else {
      console.error('Lottie library not loaded for welcome animation');
    }
  }

  if (skipWelcomeAttr || hasSeenWelcome) {
    showApp();
  } else if (isRootPage) {
    showWelcome();
  } else {
    showApp();
  }

  if (welcomeAccept) {
    welcomeAccept.addEventListener('click', () => {
      showApp();
    });
  }

  if (welcomeExit) {
    welcomeExit.addEventListener('click', () => {
      if (window.opener || window.self !== window.top) {
        window.close();
      }
      window.location.href = '/goodbye';
    });
  }

  if (heroAnimation) {
    if (window.lottie) {
      try {
        const heroAnimationPath = (window.STATIC_URL || '/static/') + 'animations/4Y28M37eMK.json';
        window.lottie.loadAnimation({
          container: heroAnimation,
          renderer: 'svg',
          loop: true,
          autoplay: true,
          path: heroAnimationPath,
          rendererSettings: {
            preserveAspectRatio: 'xMidYMid meet',
          },
        });
      } catch (error) {
        console.error('Hero Lottie loadAnimation failed', error);
      }
    } else {
      console.error('Lottie library did not load');
    }
  }

});
