document.addEventListener("DOMContentLoaded", () => {
    // 1) Pobierz listę gotowych planów z backendu
    fetch("http://localhost:8000/api/ready-plans") 
      .then(response => {
        if (!response.ok) {
          throw new Error("Błąd przy pobieraniu listy gotowych planów");
        }
        return response.json();
      })
      .then(data => {
        // data to tablica obiektów, np.:
        // [
        //   { id: 1, name: 'Plan w Tatry', description: '...' },
        //   { id: 2, name: 'Plan nad Morze', description: '...' }
        // ]
        const planyLista = document.getElementById("plany-lista");
  
        data.forEach(plan => {
          const planDiv = document.createElement("div");
          planDiv.classList.add("plan-item");
  
          const planTitle = document.createElement("h3");
          planTitle.textContent = plan.name;
  
          const planDescription = document.createElement("p");
          planDescription.textContent = plan.description;
  
          // Dodaj przycisk "Zamów PDF"
          const planButton = document.createElement("button");
          planButton.textContent = "Zamów PDF";
          planButton.style.backgroundColor = "#4CAF50";
          planButton.style.color = "white";
          planButton.style.border = "none";
          planButton.style.padding = "0.5rem 1rem";
          planButton.style.cursor = "pointer";
          planButton.style.borderRadius = "4px";
  
          // Obsługa kliknięcia "Zamów PDF"
          planButton.addEventListener("click", () => {
            // Odczytujemy adres e-mail z sekcji #global-email
            const userEmail = document.getElementById("global-email").value.trim();
  
            if (!userEmail) {
              alert("Najpierw podaj adres e-mail w sekcji na dole!");
              return;
            }
  
            // Wywołujemy endpoint, który generuje PDF gotowego planu i wysyła go na e-mail
            fetch(`/api/send-ready-plan/${plan.id}`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json"
              },
              body: JSON.stringify({ email: userEmail })
            })
              .then(response => {
                if (!response.ok) {
                  throw new Error("Błąd przy generowaniu/wysyłaniu planu PDF");
                }
                return response.json();
              })
              .then(res => {
                // Przykładowo: { message: "Plan wysłany na e-mail user@example.com" }
                alert(res.message || "Plan PDF wysłany na podany e-mail.");
              })
              .catch(err => {
                alert("Wystąpił problem: " + err.message);
              });
          });
  
          planDiv.appendChild(planTitle);
          planDiv.appendChild(planDescription);
          planDiv.appendChild(planButton);
  
          planyLista.appendChild(planDiv);
        });
      })
      .catch(err => {
        console.error("Błąd pobierania gotowych planów:", err);
      });
  
    // 2) Obsługa formularza planu indywidualnego
    const planForm = document.getElementById("plan-form");
    const wynikDiv = document.getElementById("indywidualny-plan-wynik");
  
    planForm.addEventListener("submit", (event) => {
      event.preventDefault(); // zapobiegamy przeładowaniu strony
  
      // Odczytujemy e-mail z sekcji na dole
      const userEmail = document.getElementById("global-email").value.trim();
      if (!userEmail) {
        alert("Najpierw podaj adres e-mail w sekcji na dole!");
        return;
      }
  
      // Pobieramy wartości z formularza (bez emaila, bo jest oddzielnie)
      const destinations = document.getElementById("destinations").value;
      const preferences = document.getElementById("preferences").value;
      const startDate = document.getElementById("start-date").value;
      const endDate = document.getElementById("end-date").value;
  
      // Tworzymy obiekt do wysłania w żądaniu POST
      const requestBody = {
        email: userEmail,
        destinations,
        preferences,
        startDate,
        endDate
      };
  
      // Wysyłamy zapytanie do endpointu Django, który wygeneruje PDF i go wyśle
      fetch("/api/individual-plan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      })
        .then(response => {
          if (!response.ok) {
            throw new Error("Nie udało się wygenerować indywidualnego planu PDF.");
          }
          return response.json();
        })
        .then(data => {
          /*
            Zakładamy, że backend zwraca np.:
            {
              "message": "Indywidualny plan wysłany na e-mail ...",
              "planSummary": "Opis planu...",
              "days": ["Dzień 1...", "Dzień 2..."]
            }
          */
          wynikDiv.style.display = "block";
          wynikDiv.innerHTML = `
            <h3>Wynik generowania planu</h3>
            <p><strong>${data.message}</strong></p>
            ${
              data.planSummary
                ? `<p><strong>Opis planu:</strong> ${data.planSummary}</p>`
                : ""
            }
            ${
              data.days
                ? `<ul>${data.days.map(day => `<li>${day}</li>`).join("")}</ul>`
                : ""
            }
          `;
        })
        .catch(err => {
          wynikDiv.style.display = "block";
          wynikDiv.innerHTML = `<p style="color:red;">Błąd: ${err.message}</p>`;
        });
    });
  });
  