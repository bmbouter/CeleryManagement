var CMA = (typeof CMA === "undefined" || !CMA) ? {} : CMA;
CMA.Core = (typeof CMA.Core === "undefined" || !CMA.Core) ? {} : CMA.Core;

CMA.Core.ajax = (function($) {
    var urls = {},

        loadUrls = function() {
            root_url = "/celerymanagementapp/";
            
            urls = {
                get_tasks_url: root_url + "task/all/list/",
                get_workers_url: root_url + "worker/all/list/",
                tasks_per_worker_url: root_url + "task/all/dispatched/byworker/count/",
                //task_url: root_url + "view/dispatched_tasks/",
                pending_tasks_url: root_url + "task/all/dispatched/pending/count/",
                worker_processes_url: root_url + "worker/all/subprocess/count/",
                worker_power_url: root_url + "worker/<placeHolder>/power_state/",
                query_dispatched_tasks_url: root_url + "xy_query/dispatched_tasks/",
                task_url: "/celerymanagementapp/view/task/",
                worker_url: "/celerymanagementapp/view/worker/",
                out_of_band_worker_create_url: root_url + "outofbandworker/",
                out_of_band_worker_update_url: root_url + "outofbandworker/<placeHolder>/update/",
                out_of_band_worker_delete_url: root_url + "outofbandworker/<placeHolder>/delete/",
                out_of_band_worker_power_url: root_url + "outofbandworker/<placeHolder>/power_state/",
                provider_create_url: root_url + "provider/",
                provider_delete_url: root_url + "provider/<placeHolder>/delete/",
                get_images_url: root_url + "provider/images/",
                delete_instance_url: root_url + "provider/delete_worker/",
                policy_create_url: root_url + "policy/create/",
                policy_update_url: root_url + "policy/modify/<placeHolder>/",
                policy_delete_url: root_url + "policy/delete/<placeHolder>/",
                field_info_url: root_url + "xy_query/dispatched_tasks/fieldinfo/"
            };
        },
        loadTestUrls = function() {
            var root_url = "/celerymanagementapp/site_media/test_data/";
            var post_root_url = "/celerymanagementapp/test/post/";
            
            urls = {
                get_tasks_url: root_url + "tasks.json",
                get_workers_url: root_url + "workers.json",
                tasks_per_worker_url: root_url + "tasks_per_worker.json",
                pending_tasks_url: root_url + "tasks_pending.json",
                worker_processes_url: root_url + "worker_processes.json",
                query_dispatched_tasks_url: post_root_url + "xy_query/dispatched_tasks/",
                task_url: "/celerymanagementapp/test/view/task/",
                worker_url: "/celerymanagementapp/test/view/worker/",
                chart_data_url: root_url + "chart/enumerate-1.json",
                out_of_band_worker_create_url: post_root_url + "outofbandworker/",
                out_of_band_worker_update_url: post_root_url + "outofbandworker/<placeHolder>/update/",
                out_of_band_worker_delete_url: post_root_url + "outofbandworker/<placeHolder>/delete/",
                out_of_band_worker_power_url: post_root_url + "outofbandworker/<placeHolder>/power_state/",
                provider_create_url: post_root_url + "provider/",
                provider_delete_url: post_root_url + "provider/<placeHolder>/delete/",
                get_images_url: post_root_url + "provider/images/",
                delete_instance_url: post_root_url + "provider/delete_worker/1/",
                policy_create_url: post_root_url + "policy/create/",
                policy_update_url: post_root_url + "policy/modify/<placeHolder>/",
                policy_delete_url: post_root_url + "policy/delete/<placeHolder>/"
            };
        },
        getUrls = function(){
            return urls;
        },
        getTasks = function(callbackFunction){
            $.getJSON(urls.get_tasks_url, callbackFunction);
        },
        getWorkers = function(callbackFunction){
            $.getJSON(urls.get_workers_url, callbackFunction);
        },
        getTasksPerWorker = function(callbackFunction){
            $.getJSON(urls.tasks_per_worker_url, callbackFunction);
        },
        getPendingTasks = function(callbackFunction){
            $.getJSON(urls.pending_tasks_url, callbackFunction);
        },
        getWorkerProcesses = function(callbackFunction){
            $.getJSON(urls.worker_processes_url, callbackFunction);
        },
        getFieldInfo = function(callbackFunction) {
            $.getJSON(urls.field_info_url, callbackFunction);
        },
        getDispatchedTasksData = function(query, callbackFunction) {
            $.post(urls.query_dispatched_tasks_url, query, callbackFunction, 'json');
        },
        postGetImages = function(callbackFunction){
            $.post(urls.get_images_url, $('#blankProviderForm').serialize(), callbackFunction, "json");
        },
        postDeleteInstance = function(instance, callbackFunction){
            $.post(urls.delete_instance_url.replace("<placeHolder>", instance), callbackFunction, "json");
        },
        postCreateOutOfBandWorker = function(form, callback){
            form.ajaxSubmit({
                dataType: 'json',
                url: urls.out_of_band_worker_create_url,
                success: callback
            });
        },
        postUpdateOutOfBandWorker = function(form, workerID, callback){
            form.ajaxSubmit({
                dataType: 'json',
                url: urls.out_of_band_worker_update_url.replace("<placeHolder>", workerID),
                success: callback
            });
        },
        postDeleteOutOfBandWorker = function(workerID, callback){
            $.post(urls.out_of_band_worker_delete_url.replace("<placeHolder>", workerID), {}, callback, "json");
        },
        postShutdownWorker = function(workerName, callbackFunction){
            $.post(urls.shutdown_worker_url.replace("<placeHolder>", workerName), callbackFunction, "json");
        },
        postWorkerPower = function(workerName, data, callbackFunction){
            $.post(urls.out_of_band_worker_power_url.replace("<placeHolder>", workerName), data, callbackFunction, "json");
        },
        postCreateProvider = function(form, callback){
            console.log("test");
            form.ajaxSubmit({
                dataType: 'json',
                url: urls.provider_create_url,
                success: callback
            });
        },
        postDeleteProvider = function(providerID, callback){
            $.post(urls.provider_delete_url.replace("<placeHolder>", providerID), {}, callback, "json");
        },
        postCreatePolicy = function(data, callbackFunction){
            $.post(urls.policy_create_url, data, callbackFunction, "json");
        },
        postDeletePolicy = function(policy, callbackFunction){
            $.post(urls.policy_delete_url.replace("<placeHolder>", policy), {}, callbackFunction, "json");
        },
        postUpdatePolicy = function(data, policy, callbackFunction){
            $.post(urls.policy_update_url.replace("<placeHolder>", policy), data, callbackFunction, "json");
        };

    return {
        getUrls: getUrls,
        loadUrls: loadUrls,
        loadTestUrls: loadTestUrls,
        getTasks: getTasks,
        getWorkers: getWorkers,
        getTasksPerWorker: getTasksPerWorker,
        getPendingTasks: getPendingTasks,
        getWorkerProcesses: getWorkerProcesses,
        getFieldInfo: getFieldInfo,
        postShutdownWorker: postShutdownWorker,
        getDispatchedTasksData: getDispatchedTasksData,
        postGetImages: postGetImages,
        postDeleteInstance: postDeleteInstance,
        postCreateOutOfBandWorker: postCreateOutOfBandWorker,
        postUpdateOutOfBandWorker: postUpdateOutOfBandWorker,
        postDeleteOutOfBandWorker: postDeleteOutOfBandWorker,
        postWorkerPower: postWorkerPower,
        postCreateProvider: postCreateProvider,
        postDeleteProvider: postDeleteProvider,
        postCreatePolicy: postCreatePolicy,
        postUpdatePolicy: postUpdatePolicy,
        postDeletePolicy: postDeletePolicy
    };
}(jQuery));
