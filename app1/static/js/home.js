function showPromo() {
    const probability = Math.random();
    if (probability <= 0.3) {
        const banner = document.getElementById("banner");
        banner.style.display = "inline-block";
    }
}


window.onload = showPromo;