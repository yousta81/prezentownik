const form = document.getElementById("giftForm");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const token = localStorage.getItem("access_token");
    const formData = new FormData(form);

    try {
        const response = await fetch("/gifts/", {
            method: "POST",
            body: formData,
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        const result = await response.json();

        if (response.ok) {
            console.log("Gift added:", result.gift || result);
            window.location.href = "/#my_wishlist_section";
        } else {
            console.error("Error adding gift:", result);
        }

    } catch (error) {
        console.error("Request failed:", error);
    }

});

document.getElementById("cancelBtn").addEventListener("click", () => {
    window.location.href = "/#my_wishlist_section";
});