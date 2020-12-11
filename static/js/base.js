let training_ids = []
let selected_trainings = [];
let new_trainings = [];
let char_array = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"];

let Training = class{
    constructor(id, category, knowledge_area, title, link, description, free, advanced){
        this.id = id;
        this.category = category;
        this.knowledge_area = knowledge_area;
        this.title = title;
        this.link = link;
        this.description = description;
        this.free = free;
        this.advanced = advanced;
    }
}

let initFields = _ => {
    $('.collapsible').collapsible();
    $('select').formSelect();
    $("#add_training_form").hide();
    //$("#training_table").hide();
}

let build_table = _ => {
    $("#training_table").show();
    let training_tbody = $("#training_tbody");
    training_tbody.empty();

    selected_trainings.forEach(train => {
        training_tbody.append(`<tr> 
        <td style="vertical-align: top;">${train.category}</td>
        <td style="vertical-align: top;">${train.knowledge_area}</td>
        <td style="vertical-align: top;">${train.title}</td>
        <td style="vertical-align: top;"><i class="material-icons" style='cursor: pointer;' onClick="removeTraining(${train.id})">delete</i></td>
        </tr>`); 
    }); 
    new_trainings.forEach(train => {
        training_tbody.append(`<tr> 
        <td style="vertical-align: top;">${train.category}</td>
        <td style="vertical-align: top;">${train.knowledge_area}</td>
        <td style="vertical-align: top;">${train.title}</td>
        <td style="vertical-align: top;"><i class="material-icons" style='cursor: pointer;' onClick="removeTraining('${train.id}')">delete</i></td>
        </tr>`); 
    }); 
}

let removeTraining = (training_id) => {
    if(isNaN(training_id))
        new_trainings = new_trainings.filter(training => training.id != training_id);
    else{
        training_ids = training_ids.filter(id => id != training_id);
        selected_trainings = selected_trainings.filter(training => training.id != training_id);
        $(`#training_check${training_id}`).prop("checked", false);
    }
    build_table();
}

let addTraining = _ => {
    let training = new Training(char_array[new_trainings.length], $("#category").val(), $("#knowledge_area").val(), $("#title").val(), $("#link").val(), $("#description").val(), ($('#free').prop('checked') ? 1 : 0), 0);
    new_trainings.push(training);
    build_table();
}

const validateEmail = (email)  => {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email.toLowerCase());
}

let failedValidation = (message) =>{
    $("#validation_message").text(message);
    $("submit_form").prop("disabled", false);
}

let validateForm = async _ =>{
    $("submit_form").prop("disabled", true);
    let email = $("#email").val();
    if($("#approver").val() == "0"){        
        return failedValidation("Please pick your approver");
    }
    if($("#email").val() == ""){
        return failedValidation("Please enter a valid name");
    }
    if(validateEmail(email) && email.slice(email.search('@')+1) == "ge.com"){
        let user_check = await verify_user();
        if(user_check == 200){ 
            $("#validation_message").text();
            await submit_form();
        }
        else{ 
            return failedValidation("You have already submitted your list");
        }
    }
    else{
        return failedValidation("Please enter valid ge email");
    }
}

let verify_user = async _ => {
    let email = $("#email").val();
    let url = "/verifyuser" + "?email=" + email;
    const check = await fetch(url)
    const res = await check.status;
    return res;                    
}

let submit_form = async () =>{
    let submit_json = {};
    submit_json.name = $("#name").val();
    submit_json.email = $("#email").val();
    submit_json.approver_id = $("#approver").val();
    submit_json.selected_training_ids = training_ids;
    submit_json.new_trainings = new_trainings;
    
    const response = await fetch("/submit", {
        method: 'POST', 
        mode: 'same-origin',
        cache: 'no-cache',
        credentials: 'same-origin', 
        headers: {
          'Content-Type': 'application/json'
        },
        redirect: 'follow', 
        referrerPolicy: 'no-referrer',
        body: JSON.stringify(submit_json)
      });
    const status_code = await response.status;
    if(status_code == 200)
        $(location).attr('href',"/success");
    else
        $(location).attr('href',"/failure");
      //console.log(response.json()); // parses JSON response into native JavaScript objects
}

$(document).ready(() => {
    initFields();
    $("#show_training_form").click(e => {
        e.preventDefault();
        $("#add_training_form").show();
    });
    $("#add_training").click(e => {
        e.preventDefault();
        addTraining();
    });
    $(".add_training_check").click(e => {
        let checkbox = $(e.target);
        if(checkbox.prop("checked")){
            training_ids.push(checkbox.attr("training_id"));
            let training = new Training(checkbox.attr("training_id"), checkbox.attr("training_category"), checkbox.attr("training_knowledge_area"), checkbox.attr("training_title"), "", "", 0, 0);
            selected_trainings.push(training);
            build_table();
        }
        else{
            removeTraining(checkbox.attr("training_id"));
        }
    });
    $("#submit_form").click(e => {
        e.preventDefault();
        validateForm();
    });
});

window.onscroll = function() {changeDivPosition()};

var header = document.getElementById("training_table");
var sticky = header.offsetTop;

function changeDivPosition() {
  if (window.pageYOffset > sticky) {
    header.classList.add("sticky");
  } else {
    header.classList.remove("sticky");
  }
}