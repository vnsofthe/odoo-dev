openerp.web_camera = function(instance){
	var _t = instance.web._t,
	_lt = instance.web._lt;
	var Enable_change_button;
	var width;
	var height
	var check;
	var canvas;
	var context;
	var videoObj;
	var video;
	var errBack;
	var QWeb = instance.web.qweb;
    instance.web.form.widgets.add('webcam', 'instance.web.form.webcam_Mywidget');
    instance.web.form.webcam_Mywidget = instance.web.form.FieldBinaryImage.extend(
    			{
    			template : 'webcam_temp',
    			placeholder: "/web/static/src/img/placeholder.png",
    			    render_value: function() {
    			        var self = this;
    			        var url;
    			        			        
    			        width=this.options.width;
    			        height=this.options.height;
    			        if (this.get('value') && !instance.web.form.is_bin_size(this.get('value'))) {
    			        	check="yes";
    			        	if(self.field_manager.get("actual_mode")=='edit'){
    			        		var self=this;
    			        		$("#save_as").children("img").remove();
    			        		$('#change_snap').attr('disabled',false);
    			        	}
    			        	
    			        	$('#snap').hide();
    			        	$('canvas').hide();
    			        	$('video').hide();
    			        	$("#change_snap").children("img").hide();
    			            	url = 'data:image/png;base64,' + this.get('value');
    			            
    			            
    			        } 
    			        else if (this.get('value')) {
    			        	$("#save_as").children("img").remove();
    			        	check="yes";
    			        	
    			            var id = JSON.stringify(this.view.datarecord.id || null);
    			            var field = this.name;
    			            if (this.options.preview_image)
    			                field = this.options.preview_image;
    			            
    			            url = this.session.url('/web/binary/image', {
    			                                        model: this.view.dataset.model,
    			                                        id: id,
    			                                        field: field,
    			                                        t: (new Date().getTime()),
    			            });
    			            if(self.field_manager.get("actual_mode")=='edit')
    			            	{
    			            	var self=this;
    			            	$('#change_snap').attr("disabled",false);

    			            	}
    			            $('#snap').hide();
    			            $('#canvas').hide();
    			            $('#video').hide();
    			        }
    			        else {
    			        	var self=this
    			        	first="yes";
    			        	$("#save_as").children("img").remove();
    			        	$("#save_button").hide();
    			        	if(check=="yes")
			    			        	{
    			        				$("#video").show();
    			        				$("#change_snap").attr("disabled",true);
    			        				$("#snap").show();    			        				
			    			        	}
    			        	 self.on_start_camera();
    			        	 url = this.placeholder;
    			            }
    			         
    			        var $img = $(QWeb.render("FieldBinaryImage-camimg", { widget: this, url: url }));
    			        this.$el.find('> img').remove();
    			        this.$el.prepend($img);
    			        $img.load(function() {
    			            if (! self.options.size)
    			                return;
    			            $img.css("max-width", "" + self.options.size[0] + "px");
    			            $img.css("max-height", "" + self.options.size[1] + "px");
    			            $img.css("margin-left", "" + (self.options.size[0] - $img.width()) / 2 + "px");
    			            $img.css("margin-top", "" + (self.options.size[1] - $img.height()) / 2 + "px");
    			        });
    			        if(Enable_change_button == "yes")
    			        {
    			        	$("#change_snap").attr("disabled",false);
    			        	Enable_change_button="no"
    			        }
    			        
    			        
    			        $("#save_as").children("img").remove();
    			        $("#change_snap").children("img").remove();
    			        $("#snap").click(function(){
    			        	
    			        	$('#canvas').attr('width', video.videoWidth);
    			        	$('#canvas').attr('height', video.videoHeight);
    			        	$("#change_snap").attr("disabled",false);
    			        	context.drawImage(video, 0, 0);
			            	var image = new Image();
			            	image_src = canvas.toDataURL("image/png");
			            	$("#canvas").hide();
			            	$("#video").hide();
			            	$('#snap').hide();
			            	file_base64=image_src.replace("data:image/png;base64,", "");
			                self.on_file_uploaded_and_valid1(file_base64);
			                $("#change_snap").children("img").hide();
			                $("#save_button").show()
			                $("#save_as").children("img").remove();
			           });
    			        $("#change_snap").click(function(){
    			        	self.on_start_camera();
    			        	$("#save_as").children("img").remove();
    			        	$("#change_snap").attr("disabled",true);
    			        	  $('#snap').show();
    			        	  $('#video').show();
    			          });
    			    },
    			    on_start_camera:function()
    			    {
    			    	canvas = document.getElementById("canvas");
	            		context = canvas.getContext("2d");
	            		video = document.getElementById("video");
	            		videoObj = { "video": true };
	            		errBack = function(error) {
	            			console.log("Video capture error: ", error.code); 
	            		};
	            	
	            		if(navigator.getUserMedia) { 
		            		
		            		navigator.getUserMedia(videoObj, function(stream) {
		            			video.src = stream;
		            			video.play();
		            		}, errBack);
		            	} else if(navigator.webkitGetUserMedia) { 
		            		
		            		navigator.webkitGetUserMedia(videoObj, function(stream){
		            			video.src = window.webkitURL.createObjectURL(stream);
		            			video.play();
		            		}, errBack);
		            		
		            	}
		            	
		            	else if (navigator.mozGetUserMedia){     				        			
		        			navigator.mozGetUserMedia(videoObj, function(stream){
		        				video.mozSrcObject = stream;
			        			video.play();
		            		}, errBack);
		        		}
		        		
		        		else if (navigator.msGetUserMedia){
		        			navigator.msGetUserMedia({video:true, audio:false}, gotStream, noStream);
		        			video.src = stream;
		        			video.play();
		            	}
    			    },
    			    
    			    on_file_uploaded_and_valid: function(size, name, content_type, file_base64) {
    			    	
    			    	Enable_change_button="yes";
    			        this.internal_set_value(file_base64);
    			        this.binary_value = true;
    			        this.render_value();
    			        this.set_filename(name);
    			    },
    			    
    			    on_file_uploaded_and_valid1: function(file_base64) {
    			    	
    			        this.internal_set_value(file_base64);
    			        this.binary_value = true;
    			        this.render_value();
    			        this.set_filename(name);
    			    },
    			    on_clear: function() {
    			    	
    			        this._super.apply(this, arguments);
    			        this.render_value();
    			        this.set_filename('');
    			    }
    			
    		});
}
