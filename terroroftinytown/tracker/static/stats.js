(function(){

"use strict";

var WSController = function(endpoint){
	this.endpoint = endpoint;
	this.initWebSocket();
	this.stats = {
		'live': [],
		'lifetime': {},
		'global': [0, 0],
		'project': {},
		'currentScanRate': 0
	};
	this.reconnectTimer = null;
	this.scanRateBucket = [];
	this.prevScanBucketIndex = 0;
	this.updateInterval = 500;

	for (var i = 0; i < 60; i++) {
		this.scanRateBucket.push(0);
	}
};

WSController.prototype.initWebSocket = function () {
	var scheme = window.location.protocol == "https:" ? "wss://" : "ws://";
	this.ws = new WebSocket("" + scheme + window.location.host + this.endpoint);
	this.ws.onmessage = this._onmessage.bind(this);
	this.ws.onopen = this.onConnect.bind(this);
	this.ws.onerror = this.onDisconnect.bind(this);
	this.ws.onclose = this.onDisconnect.bind(this);
}

WSController.prototype._onmessage = function(evt){
	var message = JSON.parse(evt.data);

	if(message.live){
		this.stats.live = message.live;
	}

	if(message.lifetime){
		this.stats.lifetime = message.lifetime;
	}

	if(message.global){
		this.stats.global = message.global;
	}

	if(message.project){
		this.stats.project = message.project;
	}

	if(message.live_new){
		this.stats.live.unshift(message.live_new);

		var lifetime = this.stats.lifetime[message.live_new.username];
		if(lifetime === undefined){
			lifetime = [0, 0];
			this.stats.lifetime[message.live_new.username] = lifetime;
		}
		lifetime[0] += message.live_new.found;
		lifetime[1] += message.live_new.scanned;

		this.stats.global[0] += message.live_new.found;
		this.stats.global[1] += message.live_new.scanned;

		var project = this.stats.project[message.live_new.project];
		if(lifetime === undefined){
			project = [0, 0];
			this.stats.project[message.live_new.project] = project;
		}
		project[0] += message.live_new.found;
		project[1] += message.live_new.scanned;

		var dateNow = new Date();
		var bucketIndex = dateNow.getUTCSeconds();

		if (this.prevScanBucketIndex != bucketIndex) {
			this.prevScanBucketIndex = bucketIndex;
			this.scanRateBucket[bucketIndex] = message.live_new.scanned;
		} else {
			this.scanRateBucket[bucketIndex] += message.live_new.scanned;
		}

		var sum = 0;
		for (var i = 0; i < 60; i++) {
			sum += this.scanRateBucket[i];
		}
		this.stats.currentScanRate = sum / 60.0;
	}

	this.onMessage(message);
};

WSController.prototype.onMessage = function(message){
};

WSController.prototype.onConnect = function () {
	var wsDiv = document.getElementById('websocket_message');
	wsDiv.style.display = 'none';
};

WSController.prototype.onDisconnect = function () {
	var wsDiv = document.getElementById('websocket_message');
	wsDiv.style.display = 'inherit';
	
	if (this.reconnectTimer) {
		clearTimeout(this.reconnectTimer);
	}
	this.reconnectTimer = setTimeout(this.initWebSocket.bind(this), 60000);
};


var app = angular.module("stats", []);
var lastUpdate = new Date(0);

app.constant("endpoint", "/api/live_stats");
app.constant("max_display", 30);

app.service("ws", ["endpoint", function(endpoint){
	return new WSController(endpoint);
}]);

app.filter("toArray", function(){
	return function(obj) {
		var result = [];
		angular.forEach(obj, function(val, key) {
			result.push([key, val]);
		});
		return result;
	};
});

app.controller("StatsController", ["$scope", "$filter", "ws", "max_display", function($scope, $filter, ws, max_display){
	$scope.stats = ws.stats;
	$scope.totalLimit = 30;
	$scope.recentLimit = 30;
	$scope.getScanned = function(item){
		return item[1][1];
	};
	ws.onMessage = function(){
		ws.stats.live.splice($scope.recentLimit, ws.stats.live.length);
		// somehow computing this in page cause infinite digest cycles
		$scope.lifetime = $filter("toArray")(ws.stats.lifetime);

		var dateNow = new Date();

		if (dateNow - lastUpdate > ws.updateInterval) {
			$scope.$apply();
			lastUpdate = dateNow;
			var afterDate = new Date();
			var applyDifference = afterDate - dateNow;

			if (applyDifference > 50) {
				ws.updateInterval = 1000 + Math.min(10000, applyDifference * 2);
			} else {
				ws.updateInterval = 500;
			}
		}
	};
}]);

document.getElementById('websocket_message').innerHTML = 'Sorry, live stat updates is currently unavailable.';

})();
