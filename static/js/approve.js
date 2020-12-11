let assigned_training_ids = [];

let submit_data = async () =>{
    let submit_json = {};
    submit_json.assigned_training_ids = assigned_training_ids;
    submit_json.approver_id = $("#approver_id").val();
    
    const response = await fetch("/approvetraining", {
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
}

$(document).ready(_ => {
    $('.collapsible').collapsible();
    $(".approve_training_check").click(e => {
        let checkbox = $(e.target);
        if(checkbox.prop("checked")){
            assigned_training_ids.push(checkbox.attr("training_assignment_id"));
        }
        else{
            assigned_training_ids = assigned_training_ids.filter(id => id != checkbox.attr("training_assignment_id"));
        }
    });

    $("#submit_form").click(e => {
        e.preventDefault();
        submit_data();
    });
});