function checkItemsCounter() {
   // policz liczbę prezentów zarezerwowanych i zarchiwizowanych
    const reservedCount = document.querySelectorAll('#reserved_presents_section .card').length;
    const archivedCount = document.querySelectorAll('#reserved_presents_section .card__unavailable').length;
    const paragraph = document.querySelector("#reserved_presents_section p.no_items");
    if (reservedCount - archivedCount === 0) {
      document.getElementById('items_counter').classList.add('hide');
      paragraph.classList.remove('hide');
    } else {
    document.getElementById('items_counter').classList.remove('hide');
    paragraph.classList.add('hide');
    document.getElementById('items_counter').textContent = reservedCount - archivedCount;
    }
}
// switch present categories

document.addEventListener('DOMContentLoaded', () => {
  checkItemsCounter();
});

function FadeInOut(message) {
  const overlay = document.getElementById('overlay');
  const overlay_text = document.getElementById('overlay_text');
  overlay.classList.add('fadeOut');
  overlay.classList.remove('hide');
  overlay_text.innerHTML = message;
  setTimeout(() => {
    overlay.classList.add('hide');
  }, 2000);

}

// obsługa kliknięć na przyciski rezerwacji/zwolnienia prezentu
document.addEventListener('click', async (e) => {
  const button = e.target.closest('button[name="book"], button[name="release"]');
  if (!button) return;

  const article = button.closest('article');
  const giftId = article.dataset.giftId;
  
  // AJAX toggle reservation
  const formData = new FormData();
  formData.append("gift_id", giftId);

  const res = await fetch("/reservations/toggle", {
    method: "POST",
    body: formData
  });
  // ❗ obsługa konfliktu
  if (!res.ok) {
    if (res.status === 409) {
      const error = await res.json();
      alert(`Ten prezent jest już zarezerwowany przez: ${error.detail.reserved_by}`);
    } else {
      alert("Błąd podczas zmiany rezerwacji.");
    }
    return;
  }
  const data = await res.json();

  // UI update
  const reservedSection = document.getElementById("reserved_presents_section");
  const availableSection = document.getElementById("available_presents_section");
  

  article.querySelectorAll('.card__button button').forEach(btn => btn.classList.toggle('hide'));

  if (data.status === "reserved") {
    reservedSection.insertBefore(article, reservedSection.firstChild.after(article));
    FadeInOut('Prezent zarezerwowany');
  } else if (data.status === "released") {
    availableSection.insertBefore(article, availableSection.firstChild.after(article));   
    FadeInOut('Prezent zwolniony');
  }

  checkItemsCounter();
});

//filtering presents by user


document.querySelector('.filter_buttons').addEventListener('click', (e) => {
  const button = e.target.closest('button');
  if (!button) return; // kliknięto poza buttonem

  button.classList.toggle('chosen_user');
console.log(button.dataset.user);
  const chosenUser = button.dataset.user;
const cards = document.querySelectorAll('#available_presents_section .card');
  cards.forEach(card => {
    if (card.dataset.user === chosenUser) {
      card.classList.toggle('hide');
    }
  });
});

document.getElementById("addWish").addEventListener("click", () => {
    window.location.href = "/gifts";
});

