document.addEventListener("DOMContentLoaded", () => {
    function buildReactionSummary(data) {
        const order = [
            "LOVE",
            "CARE",
            "HAHA",
            "WOW",
            "SAD",
            "ANGRY",
            "LIKE"
        ];

        const icons = {
            LOVE: "❤️",
            CARE: "🥰",
            HAHA: "😄",
            WOW: "😮",
            SAD: "😢",
            ANGRY: "😡",
            LIKE: "👍"
        };

        let html = '<span class="reaction-summary-icons">';

        let shown = 0;

        order.forEach(type => {

            if (shown >= 3)
                return;

            if (data.reaction_counts[type]) {

                html += `<span class="reaction-summary-icon">${icons[type]}</span>`;

                shown++;

            }

        });

        html += `</span> <span class="reaction-summary-total">${data.reaction_total}</span>`;

        return html;
    }
    // ==========================================
    // Facebook Reaction Hover
    // ==========================================

    document.querySelectorAll(".reaction-wrapper").forEach(wrapper => {

        const picker = wrapper.querySelector(".reaction-picker");

        let timer;

        wrapper.addEventListener("mouseenter", () => {

            clearTimeout(timer);

            picker.classList.add("show");

        });

        wrapper.addEventListener("mouseleave", () => {

            timer = setTimeout(() => {

                picker.classList.remove("show");

            }, 250);

        });

        picker.addEventListener("mouseenter", () => {

            clearTimeout(timer);

        });

        picker.addEventListener("mouseleave", () => {

            timer = setTimeout(() => {

                picker.classList.remove("show");

            }, 250);

        });

    });
    // ==========================================
    // Reaction Picker
    // ==========================================

    document.querySelectorAll(".reaction").forEach(reaction => {

        reaction.addEventListener("click", async function () {

            const wrapper = this.closest(".reaction-wrapper");
            const button = wrapper.querySelector(".like-btn");

            const postId = button.dataset.post;

            const response = await fetch(
                `/api/community/${communityId}/posts/${postId}/like`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        reaction: this.dataset.reaction
                    })
                }
            );

            const data = await response.json();

            if (!data.success)
                return;

            if (data.removed) {

                button.dataset.reaction = "";

                button.querySelector(".reaction-icon").textContent = "👍";
                button.querySelector(".reaction-text").textContent = "Like";

            } else {

                button.dataset.reaction = data.reaction;

                button.querySelector(".reaction-icon").textContent = data.icon;
                button.querySelector(".reaction-text").textContent = data.text;

            }

            document.getElementById(
                `likes-count-${postId}`
            ).innerHTML =
                buildReactionSummary(data);
        });

    });

    // ==========================================
    // Click Like Button
    // ==========================================

    document.querySelectorAll(".like-btn").forEach(button => {

        button.addEventListener("click", async function () {

            const postId = this.dataset.post;

            const reaction =
                this.dataset.reaction || "LIKE";

            const response = await fetch(
                `/api/community/${communityId}/posts/${postId}/like`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        reaction: reaction
                    })
                }
            );

            const data = await response.json();

            if (!data.success)
                return;

            if (data.removed) {

                this.dataset.reaction = "";

                this.querySelector(".reaction-icon").textContent = "👍";
                this.querySelector(".reaction-text").textContent = "Like";

            } else {

                this.dataset.reaction = data.reaction;

                this.querySelector(".reaction-icon").textContent = data.icon;
                this.querySelector(".reaction-text").textContent = data.text;

            }

            document.getElementById(
                `likes-count-${postId}`
            ).innerHTML =
                buildReactionSummary(data);

        });

    });
    // ==========================================
    // View Reactions
    // ==========================================

    document.querySelectorAll(".post-reactions-count").forEach(item=>{

        item.addEventListener("click", async function(){

            const postId=this.dataset.post;

            const response=await fetch(`/api/posts/${postId}/reactions`);

            const reactions=await response.json();

            const list=document.getElementById("reactions-list");
            const tabs=document.getElementById("reaction-tabs");

            list.innerHTML="";
            tabs.innerHTML="";

            if(reactions.length===0){

                list.innerHTML="<p class='text-center text-muted'>No reactions yet.</p>";

                new bootstrap.Modal(
                    document.getElementById("reactionsModal")
                ).show();

                return;
            }

            const icons={

                LIKE:"👍",
                LOVE:"❤️",
                CARE:"🥰",
                HAHA:"😄",
                WOW:"😮",
                SAD:"😢",
                ANGRY:"😡"

            };

            function render(type){

                list.innerHTML="";

                let filtered=reactions;

                if(type!=="ALL"){

                    filtered=reactions.filter(
                        r=>r.reaction===type
                    );

                }

                filtered.forEach(user=>{

                    list.insertAdjacentHTML(
                        "beforeend",
                        `
                        <div class="reaction-user">

                            <img
                                src="${
                                    user.profile_image
                                    ? "/static/uploads/"+user.profile_image
                                    : "/static/images/default-profile.jpg"
                                }"
                                class="reaction-user-avatar">

                            <strong>${user.username}</strong>

                            <span class="ms-auto fs-4">
                                ${icons[user.reaction]}
                            </span>

                        </div>
                        `
                    );

                });

            }

            // ---------- ALL TAB ----------

            tabs.insertAdjacentHTML(
                "beforeend",
                `
                <button
                    class="reaction-tab active"
                    data-type="ALL">

                    All (${reactions.length})

                </button>
                `
            );

            // ---------- Individual tabs ----------

            Object.keys(icons).forEach(type=>{

                const count=reactions.filter(
                    r=>r.reaction===type
                ).length;

                if(count===0)
                    return;

                tabs.insertAdjacentHTML(
                    "beforeend",
                    `
                    <button
                        class="reaction-tab"
                        data-type="${type}">

                        ${icons[type]} ${count}

                    </button>
                    `
                );

            });

            render("ALL");

            tabs.querySelectorAll(".reaction-tab").forEach(tab=>{

                tab.addEventListener("click",function(){

                    tabs.querySelectorAll(".reaction-tab")
                        .forEach(t=>t.classList.remove("active"));

                    this.classList.add("active");

                    render(this.dataset.type);

                });

            });

            new bootstrap.Modal(
                document.getElementById("reactionsModal")
            ).show();

        });

    });
});