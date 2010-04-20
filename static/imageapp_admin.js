function setupImages(path, field, upload_url,value) {
	new Asset.javascript('/static/'+path+'/plupload/plupload.full.min.js', {
		onload: function() {
			
			if (value != '') {
				var img = new Element('img', {
					'src':'/'+path+'/thumb/60/60/' + value,
					'id':'imagePreview' + field
				});
				var a = new Element('a', {
					'href':'/'+path+'/serve/' + value, 
					'class':'delete', 
					'title':'Delete image?', 
					'html':'&#10008;'
				});
				a.inject($('imageField'+field),'top');
				img.inject($('imageField'+field),'top');
				$('id_'+field).set('value', value);
			}
			
			var uploader = new plupload.Uploader({
				runtimes : 'flash,silverlight,browserplus,gears,html5,html4',
				browse_button : 'idImageAppUpload' + field,
				max_file_size : '10mb',
				multipart:true,
				multi_selection:false,
				url : upload_url,
				multipart_params: {},
				flash_swf_url : '/static/'+path+'/plupload/plupload.flash.swf',
				silverlight_xap_url : '/static/'+path+'/plupload/plupload.silverlight.xap',
				filters : [
					{title : "Image files", extensions : "jpg,gif,png"}
				],
				resize : {width : 2000, height : 2000, quality : 95}
			});
			
			uploader.bind('QueueChanged', function(up, file) {
				uploader.start();
			});

			uploader.bind('FileUploaded', function(up, file, response) {
				var data = JSON.decode(response.response);
				uploader.settings.url = data.newurl;

				if ($('imagePreview'+field))
					$('imagePreview'+field).set('src', '/'+path+'/thumb/60/60/' + data.key);
				else {
					var img = new Element('img', {
						'src':'/'+path+'/thumb/60/60/' + data.key,
						'id':'imagePreview' + field
					});
					var a = new Element('a', {
						'href':'/'+path+'/serve/' + data.key, 
						'class':'delete', 
						'title':'Delete image?', 
						'html':'&#10008;'
					});
					a.inject($('imageField'+field),'top');
					img.inject($('imageField'+field),'top');
				}
				$('id_'+field).set('value', data.key);
			});
		
			uploader.init();
		}
	});
}