
$(document).ready(function() {
	var handle_data = function(data) {
		//console.log("Success: " + JSON.stringify(data, undefined, 2));
		
		//var tbody = document.getElementsByName("cluster-list")[0];
		var table = $("<table id=\"cluster-list\"></table>");
		
		var field_row = $("<tr></tr>");
		fields = ["Node ID", "Processes", "Master", "Last Contact"];
		for(index in fields)
		{
			field = fields[index];
			
			field_row.append($("<th></th>").text(field));
		}
		table.append(field_row);
		
		cluster_info = data.cluster_info;
		for(key in cluster_info)
		{
			var node = cluster_info[key];
			
			var row = $("<tr></tr>");
			
			row.append($("<td></td>").text(node.name));
			row.append($("<td></td>").text(node.processes.join(", ")));
			row.append($("<td></td>").text(node.master));
			row.append($("<td></td>").text(node.last_contact_seconds + " seconds ago"));
			
			if(node.last_contact_seconds > 10.0)
			{
				row.addClass("old-info");
			}
			
			table.append(row);
		}
		
		block = $(".cluster-list-block");
		block.html(table);
	};
	
	var handle_error = function(jqxhr, textStatus, error) {
		var err = textStatus + ", " + error;
		console.log( "Request Failed: " + err );
	};
	
	var poll = function() {
		$.getJSON("api/octo-dad.json")
			.done(handle_data)
			.fail(handle_error);
		
		start_polling();
	}
	
	var start_polling = function() {
		setTimeout(poll, 1000);
	}
	
	start_polling();
});
