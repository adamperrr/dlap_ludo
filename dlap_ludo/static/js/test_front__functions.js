import * as promisesCollector from './test_front__promises.js'

export function errorsFromResponseBodyToArray(responseBody) {
    return Object.keys(responseBody).map( key => {
        let forEachResult = [];
        if (Array.isArray(responseBody[key])) {
            responseBody[key].forEach(item => {
                forEachResult = [...forEachResult, `${key}: ${item}`];
            });
        }
        else {
            forEachResult = [...forEachResult, `${key}: ${responseBody[key]}`];
        }
        console.log('[errorsFromResponseBodyToArray()]', forEachResult);
        return forEachResult;
    });
}

export function displayErrors(errors_div_id, errors) {
    let errors_div = document.getElementById(errors_div_id);
    errors_div.innerHTML = ''; // Remove all child elements of old error list

    let ul = document.createElement('ul');
    ul.classList.add('list-group', 'm-2');

    errors.forEach(function(entry) {
        let li = document.createElement("li");
        li.classList.add('list-group-item', 'list-group-item-danger');

        let li_text = document.createTextNode(entry);
        li.appendChild(li_text);
        ul.appendChild(li);
    });

    errors_div.appendChild(ul);
    errors_div.classList.remove("d-none");
}

export function creationState() {
    document.getElementById("create_room__container").classList.remove("d-none");
    document.getElementById("join_room__container").classList.remove("d-none");
//------------------------------------------------------------------------
    document.getElementById("room_name__header").classList.remove("d-none");
    document.getElementById("room_name__header").classList.add("d-none");
    document.getElementById("chat__container").classList.add("d-none");
    document.getElementById("player_data__container").classList.add("d-none");
    document.getElementById("game__container").classList.add("d-none");
}

export function gameState() {
    document.getElementById("create_room__container").classList.add("d-none");
    document.getElementById("join_room__container").classList.add("d-none");
//------------------------------------------------------------------------
    document.getElementById("room_name__header").classList.remove("d-none");
    document.getElementById("room_name__title").textContent = sessionStorage.getItem("roomName");

    document.getElementById("chat__container").classList.remove("d-none");

    document.getElementById("player_data__container").classList.remove("d-none");
    document.querySelector("#player_data__value_room_name div:first-child").textContent = sessionStorage.getItem("roomName");
    document.querySelector("#player_data__value_player_username div:first-child").textContent = sessionStorage.getItem("playerUsername");
    document.querySelector("#player_data__value_token div:first-child").textContent = sessionStorage.getItem("token");
    let isAdmin = sessionStorage.getItem("isAdmin");
    document.querySelector("#player_data__value_is_admin div:first-child").textContent = isAdmin;
    document.querySelector("#player_data__value_is_player div:first-child").textContent = sessionStorage.getItem("isPlayer");
    document.querySelector("#player_data__value_color div:first-child").textContent = sessionStorage.getItem("color");

    document.getElementById("game__container").classList.remove("d-none");
    if(isAdmin == 'true') {
        console.log('[gameState()] enabling')
        document.getElementById("game__stop_game_button").disabled = false;
    }
}

export function changeContainersState() {
    let tokenOk = false;
    let request_message = {
        'player_username': sessionStorage.getItem("playerUsername"),
        'token': sessionStorage.getItem("token")
    };

    promisesCollector.checkTokenPromise(request_message)
    .then(
        r =>  r.json().then(
            data => ({ok: r.ok, status: r.status, body: data})
        )
    )
    .then(response => {
        if(response.ok) {
            tokenOk = response.body.token_ok;
            if(tokenOk) {
                gameState();
            }
            else {
                creationState();
                sessionStorage.clear();
            }
        }
        else {
            console.error("[changeContainersState (!response.ok)]", response);
        }
    })
    .catch(error => {
        // Won't catch statuses 400, 404, 500 - it's only for connection errors
        console.error("[changeContainersState (catch)]", error);
     });
}
