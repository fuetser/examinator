// to change arrows on buttons to open/close comment for question
const collapseButtons = Array.from(document.getElementsByClassName("collapse-button"))
collapseButtons.map(
    btn => btn.addEventListener("click", e => {
        if(btn.parentElement.classList.contains("collapsed")){
            btn.classList.remove("bi-caret-up-square-fill")
            btn.classList.add("bi-caret-down-square-fill")
        } else {
            btn.classList.remove("bi-caret-down-square-fill")
            btn.classList.add("bi-caret-up-square-fill")
        }
    })
)
// to change the fill of the marked buttons
const markedButtons = Array.from(document.getElementsByClassName("marked-button"))
markedButtons.map(
    btn => btn.addEventListener("click", e => {
        if(btn.classList.contains("bi-star")){
            btn.classList.remove("bi-star")
            btn.classList.add("bi-star-fill")
        } else if(btn.classList.contains("bi-star-fill")) {
            btn.classList.remove("bi-star-fill")
            btn.classList.add("bi-star")
        }
    })
)

function markQuestion(question_id) {
    $.post("/mark", {question_id}, data => {})
}


function deleteQuestion(question_id) {
    $.post("/delete_question", {question_id}, data => {
        window.location = document.referrer
    })
}
