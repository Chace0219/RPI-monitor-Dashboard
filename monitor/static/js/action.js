var socket;

$(document).ready(function() {
	// Use a "/test" namespace.
	// An application can open a connection on multiple namespaces, and
	// Socket.IO will multiplex all those connections on a single
	// physical channel. If you don't care about multiple channels, you
	// can set the namespace to an empty string.
	namespace = '/status';
	// Connect to the Socket.IO server.
	// The connection URL has the following format:
	//     http[s]://<domain>:<port>[/<namespace>]
	socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
	// Event handler for new connections.
	// The callback function is invoked when a connection with the
	// server is established.
	//socket.on('connect', function() {
	//	socket.emit('my_event', {data: 'I\'m connected!'});
	//});
	// Event handler for server sent data.
	// The callback function is invoked whenever the server emits data
	// to the client. The data is then displayed in the "Received"
	// section of the page.
	
	socket.on('status', function(msg) {
		console.log ("connected");
		
		load_Data(msg.data);

	});

	function load_Data(json)
    {
        var display_data = JSON.parse(json);
        console.log(display_data);
        var html ='';
        display_data.forEach(function(item, idx)
        { 
            html +='<tr id="'+item.uniqueid+'">';
            html +='<td class="edit" data-name="description">'+item.description+'</td>';
            html +='<td class="edit" data-name="ipaddr">'+item.ipaddr+'</td>';
            html +='<td class="edit" data-name="gpio">'+item.gpio+'</td>';
            html +='<td>'+item.status+'</td>';
            html +='<td class="edit" data-name="cycle">'+item.cycle+'</td>';
            html +='<td class="edit" data-name="uid">'+item.uid+'</td>';
            html +='<td class="edit" data-name="pwd">'+item.pwd+'</td>';
            html +='<td class="function_buttons"><a data-id="' + item.uniqueid + '" class="btn btn-info function_reboot">Reboot</a><a data-id="' + item.uniqueid + '" class="btn btn-success function_power">Shut</a><a data-id="' + item.uniqueid + '" class="btn btn-danger function_delete">Delete</a></td>';
            html +='</tr>';    
        });
        
        $("#dataTables-event tbody").html('');
        $("#dataTables-event tbody").append(html); 

        /*$('#dataTables-event').DataTable
        ({
		    destroy: true,
		    pageLength: 10,
	        responsive: true,
	 		ordering: false
		});*/

        

    }


});
