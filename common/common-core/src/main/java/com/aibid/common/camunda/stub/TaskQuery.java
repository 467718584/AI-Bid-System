package com.aibid.common.camunda.stub;

import java.io.Serializable;
import java.util.List;

public class TaskQuery implements Serializable {
    public TaskQuery taskAssignee(String assignee) { return this; }
    public TaskQuery taskUnassigned() { return this; }
    public TaskQuery processInstanceId(String instanceId) { return this; }
    public TaskQuery taskId(String taskId) { return this; }
    public List<Task> list() { return null; }
    public Task singleResult() { return null; }
}
