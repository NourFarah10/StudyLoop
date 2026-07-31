document.addEventListener("DOMContentLoaded", () => {
    function buildCommentReactionSummary(data) {

        // Comments from the initial "load comments" endpoint may only
        // have a plain reaction_total with no per-type breakdown.
        // Only the live reaction-click response includes reaction_counts.
        const counts = data.reaction_counts || {};

        let html = "";
        if (counts.LOVE) html += "❤️ ";
        if (counts.CARE) html += "🥰 ";
        if (counts.HAHA) html += "😄 ";
        if (counts.WOW) html += "😮 ";
        if (counts.SAD) html += "😢 ";
        if (counts.ANGRY) html += "😡 ";
        if (counts.LIKE) html += "👍 ";

        // No breakdown available at all — fall back to a generic thumbs-up
        // so we still show something sensible for reaction_total > 0.
        if (!data.reaction_counts && data.reaction_total > 0)
            html += "👍 ";

        if (data.reaction_total > 0)
            html += data.reaction_total;

        return html;
    }
    // ===============================
    // Profile Image
    // ===============================

    function profileImage(image) {

        // The `users.profile_image` column defaults to the literal string
        // "default-profile.jpg" rather than NULL/empty, so this is always
        // truthy even when the user never uploaded a picture — without
        // this check it would incorrectly look for that file inside
        // static/uploads/ instead of static/images/, where it actually
        // lives.
        if (image && image !== "default-profile.jpg")
            return `/static/uploads/${image}`;

        return "/static/images/default-profile.jpg";

    }

    // ===============================
    // Comment HTML
    // ===============================

    function commentHTML(comment) {

        const replies = comment.replies || [];

        return `
            <div
                class="comment"
                data-id="${comment.id}"
                data-post="${comment.post_id}">
            <img
                src="${profileImage(comment.profile_image)}"
                class="comment-avatar">

            <div class="comment-body">

                <div class="comment-header">

                    <div>

                        <strong>${comment.username}</strong>

                        <small class="comment-time">

                            ${comment.created_at}

                        </small>

                    </div>

                    ${
                        comment.user_id === currentUserId ?

                        `

                        <div class="post-owner-actions">

                            <button
                                class="post-action-btn edit-btn edit-comment-btn"
                          data-comment="${comment.id}"
                                title="Edit">

                                <i class="bi bi-pencil-square"></i>

                            </button>

                            <button
                                class="post-action-btn delete-btn delete-comment-btn"
                          data-comment="${comment.id}"
                                title="Delete">

                                <i class="bi bi-trash"></i>

                            </button>

                        </div>

                        `

                        :

                        ""

                    }

                </div>

                <div class="comment-bubble">

                    <span class="comment-content">
                        ${comment.content}
                    </span>

                </div>

                <div class="comment-actions">

                    <div class="comment-reaction-wrapper">

                        <div class="comment-reaction-picker">

                            <span class="comment-reaction"
                          data-comment="${comment.id}"
                                data-reaction="LIKE"
                                data-icon="👍"
                                data-text="Like">👍</span>

                            <span class="comment-reaction"
                          data-comment="${comment.id}"
                                data-reaction="LOVE"
                                data-icon="❤️"
                                data-text="Love">❤️</span>

                            <span class="comment-reaction"
                          data-comment="${comment.id}"
                                data-reaction="CARE"
                                data-icon="🥰"
                                data-text="Care">🥰</span>

                            <span class="comment-reaction"
                                data-comment="${comment.id}"
                                data-reaction="HAHA"
                                data-icon="😄"
                                data-text="Haha">😄</span>

                            <span class="comment-reaction"
                                data-comment="${comment.id}"
                                data-reaction="WOW"
                                data-icon="😮"
                                data-text="Wow">😮</span>

                            <span class="comment-reaction"
                                data-comment="${comment.id}"
                                data-reaction="SAD"
                                data-icon="😢"
                                data-text="Sad">😢</span>

                            <span class="comment-reaction"
                                data-comment="${comment.id}"
                                data-reaction="ANGRY"
                                data-icon="😡"
                                data-text="Angry">😡</span>

                        </div>

                        <button
                            class="comment-like-btn"
                            data-comment="${comment.id}">

                            <span class="reaction-icon">
                                ${
                                    comment.user_reaction === "LOVE" ? "❤️" :
                                    comment.user_reaction === "CARE" ? "🥰" :
                                    comment.user_reaction === "HAHA" ? "😄" :
                                    comment.user_reaction === "WOW" ? "😮" :
                                    comment.user_reaction === "SAD" ? "😢" :
                                    comment.user_reaction === "ANGRY" ? "😡" :
                                    "👍"
                                }
                            </span>

                            <span class="reaction-text">
                                ${
                                    comment.user_reaction || "Like"
                                }
                            </span>

                        </button>

                    </div>

                    <button
                        class="reply-btn"
                        data-comment="${comment.id}">

                        Reply

                    </button>

                </div>

                <div
                    class="comment-reaction-count"
                    data-comment="${comment.id}">

                    ${
                        comment.reaction_total > 0
                        ? buildCommentReactionSummary(comment)
                        : ""
                    }

                </div>

                <!-- Reply form -->

                <div
                    class="reply-form"
                    id="reply-form-${comment.id}"
                    style="display:none;">

                    <input
                        type="text"
                        class="reply-input"
                        placeholder="Write a reply...">

                    <button
                        class="reply-submit-btn"
                        data-comment="${comment.id}"
                        data-post="${comment.post_id}">

                        Reply

                    </button>

                    <button
                        type="button"
                        class="comment-cancel-btn reply-cancel-btn"
                        data-comment="${comment.id}">

                        Cancel

                    </button>

                </div>

                <!-- Replies -->

                <div class="reply-toggle-wrapper">

                    ${
                        replies.length > 0 ?

                        `
                        <button
                            class="view-replies-btn"
                            data-comment="${comment.id}">

                            View ${replies.length}
                            ${replies.length===1 ? "reply" : "replies"}

                        </button>
                        `

                        :

                        ""

                    }

                </div>

                <div
                    class="replies"
                    id="replies-${comment.id}"
                    style="display:none;">

                    ${replies.map(reply => commentHTML(reply)).join("")}

                </div>

            </div>

        </div>

        `;
    }

    // ===============================
    // Load Comments
    // ===============================

    async function loadComments(postId) {

        const list =
            document.querySelector(`#comments-${postId} .comments-list`);

        list.innerHTML = "";

        const response = await fetch(
            `/api/community/${communityId}/posts/${postId}/comments`
        );

        const comments = await response.json();

        if (comments.length === 0) {

            list.innerHTML =
                "<p class='text-muted'>No comments yet.</p>";

            return;

        }

        comments.forEach(comment => {

            list.insertAdjacentHTML(
                "beforeend",
                commentHTML(comment)
            );

        });

    }

    // ===============================
    // Toggle Comments
    // ===============================

    document.querySelectorAll(".comment-btn").forEach(button => {

        button.addEventListener("click", async function () {

            const postId = this.dataset.post;

            const section =
                document.getElementById(`comments-${postId}`);

            if (section.classList.contains("show")) {

                section.classList.remove("show");
                return;

            }

            section.classList.add("show");

            await loadComments(postId);

            section.querySelector("input").focus();

        });

    });

    // ===============================
    // Add Comment
    // ===============================

    document.querySelectorAll(".comment-form").forEach(form => {

        form.addEventListener("submit", async function(e){

            e.preventDefault();

            const postId = this.dataset.post;

            const input = this.querySelector("input");

            const content = input.value.trim();

            if(content==="")
                return;

            const response = await fetch(

                `/api/community/${communityId}/posts/${postId}/comment`,

                {

                    method:"POST",

                    headers:{
                        "Content-Type":"application/json"
                    },

                    body:JSON.stringify({
                        content:content
                    })

                }

            );

            const data = await response.json();

            if(!data.success)
                return;

            const list =
                document.querySelector(`#comments-${postId} .comments-list`);

            if(list.querySelector(".text-muted"))
                list.innerHTML="";

            list.insertAdjacentHTML(
                "beforeend",
                commentHTML(data.comment)
            );

            input.value="";

            document.getElementById(
                `comments-count-${postId}`
            ).textContent =
                `💬 ${data.count} Comments`;

        });

    });

    // ===============================
    // Edit Comment
    // ===============================

    document.addEventListener("click", async function (e) {

        // =========================================
        // Start Editing
        // =========================================
        if (e.target.closest(".edit-comment-btn")) {

            const button = e.target.closest(".edit-comment-btn");

            const comment =
                button.closest(".comment");

            const content =
                comment.querySelector(".comment-content");

            const oldText =
                content.textContent.trim();

            content.innerHTML = `
                <textarea
                    class="edit-comment-textarea"
                    rows="3"
                    placeholder="Edit your comment...">${oldText}</textarea>

                <div class="comment-edit-actions">

                    <button
                        class="comment-save-btn save-comment-btn"
                        data-id="${button.dataset.comment}">
                        Save
                    </button>

                    <button
                        type="button"
                        class="comment-cancel-btn">
                        Cancel
                    </button>

                </div>
            `;

            const textarea = content.querySelector("textarea");

            textarea.focus();

            textarea.selectionStart = textarea.value.length;
            textarea.selectionEnd = textarea.value.length;
        }

        // =========================================
        // Cancel Editing
        // =========================================
        if (e.target.classList.contains("comment-cancel-btn")) {

            const comment =
                e.target.closest(".comment");

            const textarea =
                comment.querySelector("textarea");

            comment.querySelector(".comment-content").textContent =
                textarea.defaultValue;
        }

        // =========================================
        // Save Comment
        // =========================================
        if (e.target.classList.contains("save-comment-btn")) {

            const button = e.target;

            const comment =
                button.closest(".comment");

            const textarea =
                comment.querySelector("textarea");

            const newText =
                textarea.value.trim();

            if (newText === "")
                return;

            console.log(button);
            console.log(button.dataset);
            console.log(button.dataset.comment);
            const response = await fetch(
                `/api/comments/${button.dataset.comment}/edit`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        content: newText
                    })
                }
            );

            const data = await response.json();

            if (!data.success)
                return;

            comment.querySelector(".comment-content").textContent =
                data.content;
        }

    });

    // =========================================
    // Delete Comment
    // (moved out to top level — this was previously nested inside the
    // edit-comment listener above, which re-registered a brand new
    // delete listener on every single click anywhere on the page.
    // That caused delete clicks to fire multiple times, which is what
    // was throwing "Cannot set properties of null" in the console.)
    // =========================================

    document.addEventListener("click", async function (e) {

        const button = e.target.closest(".delete-comment-btn");

        if (!button)
            return;

        if (!confirm("Delete this comment?"))
            return;

        // Grab everything we need BEFORE removing anything from the DOM
        const comment = button.closest(".comment");
        const postId = comment.dataset.post;

        // If this comment is itself a reply, remember its parent so we can
        // refresh the parent's "View X replies" toggle after removal
        const parentRepliesContainer =
            comment.parentElement.classList.contains("replies")
                ? comment.parentElement
                : null;

        const parentComment =
            parentRepliesContainer
                ? parentRepliesContainer.closest(".comment")
                : null;

        const response = await fetch(
            `/api/comments/${button.dataset.comment}/delete`,
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (!data.success)
            return;

        // remove comment
        comment.remove();

        // update comments count
        const commentsCountEl = document.getElementById(
            `comments-count-${postId}`
        );

        if (commentsCountEl)
            commentsCountEl.textContent = `💬 ${data.count} Comments`;

        // If we just deleted a reply, keep its parent's toggle button in sync
        if (parentComment) {

            const toggleWrapper =
                parentComment.querySelector(".reply-toggle-wrapper");

            const remainingReplies =
                parentRepliesContainer.querySelectorAll(":scope > .comment").length;

            if (remainingReplies === 0) {

                toggleWrapper.innerHTML = "";

            } else {

                const toggleBtn = toggleWrapper.querySelector(".view-replies-btn");

                if (toggleBtn && toggleBtn.textContent.trim().startsWith("View")) {

                    toggleBtn.textContent =
                        `View ${remainingReplies} ${remainingReplies === 1 ? "reply" : "replies"}`;
                }
            }
        }

        // show "No comments yet"
        const commentsSection =
            document.getElementById(`comments-${postId}`);

        if (commentsSection) {

            const list = commentsSection.querySelector(".comments-list");

            if (list && list.children.length === 0) {
                list.innerHTML = "<p class='text-muted'>No comments yet.</p>";
            }
        }

    });


    // =========================================
    // ESC key cancels editing / closes reply box
    // =========================================
    document.addEventListener("keydown", function(e){

        if(e.key !== "Escape")
            return;

        const textarea =
            document.querySelector(".edit-comment-textarea");

        if(textarea){

            const comment =
                textarea.closest(".comment");

            comment.querySelector(".comment-content").textContent =
                textarea.defaultValue;
        }

        const openReplyForm =
            document.querySelector(".reply-form[style*='display: block']");

        if(openReplyForm){

            openReplyForm.querySelector(".reply-input").value = "";
            openReplyForm.style.display = "none";
        }

    });

    // =========================================
    // Show Reply Box
    // =========================================

    document.addEventListener("click", function(e){

        const button = e.target.closest(".reply-btn");

        if(!button)
            return;

        // Hide every other reply form
        document.querySelectorAll(".reply-form").forEach(form=>{
            form.style.display="none";
        });

        const form =
            document.getElementById(
                `reply-form-${button.dataset.comment}`
            );

        form.style.display="block";

        form.querySelector("input").focus();

    });

    // =========================================
    // Cancel Reply
    // =========================================

    document.addEventListener("click", function(e){

        const button = e.target.closest(".reply-cancel-btn");

        if(!button)
            return;

        const form =
            document.getElementById(
                `reply-form-${button.dataset.comment}`
            );

        form.querySelector(".reply-input").value = "";
        form.style.display = "none";

    });

    // =========================================
    // Submit Reply
    // =========================================

    document.addEventListener("click", async function(e){

        const button = e.target.closest(".reply-submit-btn");

        if(!button)
            return;

        const parentCommentId = button.dataset.comment;
        const form =
            document.getElementById(
                `reply-form-${parentCommentId}`
            );

        const input =
            form.querySelector(".reply-input");

        const content =
            input.value.trim();

        if(content === "")
            return;

        const response = await fetch(

            `/api/community/${communityId}/posts/${button.closest(".comments-section").dataset.post}/comment`,

            {
                method:"POST",

                headers:{
                    "Content-Type":"application/json"
                },

                body:JSON.stringify({

                    content:content,

                    parent_comment_id:parentCommentId

                })
            }

        );

        const data = await response.json();

        if(!data.success)
            return;

        // Add reply immediately

        const comment = document.querySelector(
            `.comment[data-id="${parentCommentId}"]`
        );

        const repliesContainer = comment.querySelector(".replies");

        repliesContainer.insertAdjacentHTML(

            "beforeend",

            commentHTML(data.comment)

        );

        // Make sure the newly added reply is actually visible right away —
        // this container starts hidden and previously only got shown by
        // clicking a "View replies" button, which didn't exist yet if this
        // was the comment's first reply.
        repliesContainer.style.display = "block";

        const toggleWrapper = comment.querySelector(".reply-toggle-wrapper");

        const replyCount =
            repliesContainer.querySelectorAll(":scope > .comment").length;

        let toggleBtn = toggleWrapper.querySelector(".view-replies-btn");

        if (!toggleBtn) {

            toggleWrapper.innerHTML = `
                <button
                    class="view-replies-btn"
                    data-comment="${parentCommentId}">
                    Hide replies
                </button>
            `;

        } else if (toggleBtn.textContent.trim().startsWith("View")) {

            toggleBtn.textContent =
                `View ${replyCount} ${replyCount === 1 ? "reply" : "replies"}`;
        }

        input.value="";

        form.style.display="none";

        // Update the total comment count on the post
        const postId = button.closest(".comments-section").dataset.post;
        const commentsCountEl = document.getElementById(`comments-count-${postId}`);

        if (commentsCountEl && typeof data.count !== "undefined")
            commentsCountEl.textContent = `💬 ${data.count} Comments`;

    });

    // =========================================
    // View Replies
    // =========================================

    document.addEventListener("click",function(e){

        const btn=e.target.closest(".view-replies-btn");

        if(!btn)
            return;

        const replies = document.getElementById(
            `replies-${btn.dataset.comment}`
        );

        if(replies.style.display==="none"){

            replies.style.display="block";

            btn.textContent="Hide replies";

        }

        else{

            replies.style.display="none";

            btn.textContent="View replies";

        }

    });

    // =========================================
    // Comment Reactions
    // =========================================

    document.addEventListener("click", async function (e) {

        const reaction = e.target.closest(".comment-reaction");

        if (!reaction)
            return;

        const commentId = reaction.dataset.comment;
        const response = await fetch(
            `/api/comments/${commentId}/reaction`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    reaction: reaction.dataset.reaction
                })
            }
        );

        const data = await response.json();

        if (!data.success)
            return;

        const wrapper = reaction.closest(".comment-reaction-wrapper");

        const button = wrapper.querySelector(".comment-like-btn");

        button.dataset.reaction = data.reaction || "";

        button.querySelector(".reaction-icon").textContent = data.icon;
        button.querySelector(".reaction-text").textContent = data.text;

        wrapper.parentElement.querySelector(".comment-reaction-count").innerHTML =
            buildCommentReactionSummary(data);

    });

    // =========================================
    // View Comment Reactions
    // =========================================

    document.addEventListener("click", async function(e){

        const counter = e.target.closest(".comment-reaction-count");

        if(!counter)
            return;

        const commentId = counter.dataset.comment;

        const response = await fetch(
            `/api/comments/${commentId}/reactions`
        );

        const reactions = await response.json();

        const list =
            document.getElementById("reactions-list");

        const tabs =
            document.getElementById("reaction-tabs");

        list.innerHTML = "";
        tabs.innerHTML = "";

        if(reactions.length === 0){

            list.innerHTML =
                "<p class='text-center text-muted'>No reactions yet.</p>";

            new bootstrap.Modal(
                document.getElementById("reactionsModal")
            ).show();

            return;
        }

        const icons = {

            LIKE:"👍",
            LOVE:"❤️",
            CARE:"🥰",
            HAHA:"😄",
            WOW:"😮",
            SAD:"😢",
            ANGRY:"😡"

        };

        function render(type){

            list.innerHTML = "";

            let filtered = reactions;

            if(type !== "ALL"){

                filtered =
                    reactions.filter(r => r.reaction === type);

            }

            filtered.forEach(user=>{

                list.insertAdjacentHTML(
                    "beforeend",
                    `
                    <div class="reaction-user">

                        <img
                            src="${
                                user.profile_image
                                ? "/static/uploads/" + user.profile_image
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

        // ---------- ALL ----------

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

        // ---------- Individual Tabs ----------

        Object.keys(icons).forEach(type=>{

            const count =
                reactions.filter(r=>r.reaction===type).length;

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