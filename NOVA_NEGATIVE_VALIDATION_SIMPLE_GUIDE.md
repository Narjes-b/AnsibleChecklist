The next step means checking whether AnsibleGuard missed problems.

There are two different kinds of mistakes.

## 1. False positive

AnsibleGuard says:

```text
I found a problem.
```

But a human checks it and discovers:

```text
There is no real problem.
```

Example from Nova:

```text
AnsibleGuard: This is a long code statement.
Human: No. It is only a comment.
```

We fixed this mistake.

## 2. False negative

AnsibleGuard says nothing:

```text
This file looks clean.
```

But a human examines the file and discovers:

```text
There is a problem here, but AnsibleGuard missed it.
```

That missed problem is called a false negative.

## A very simple example

Imagine there are ten red balls inside a box.

AnsibleGuard finds eight red balls.

We check those eight and confirm they are really red.

So the findings are correct:

```text
8 reported
8 correct
Positive precision = 100%
```

But AnsibleGuard missed two other red balls.

Therefore, it is not a perfect detector.

```text
10 real red balls
8 found
2 missed
```

This is why “100% positive precision” does not mean:

```text
AnsibleGuard finds every problem.
```

It only means:

```text
The problems it reported were correct.
```

# What have we checked already?

AnsibleGuard reported 77 Nova findings:

```text
38 complex expressions
39 long statements
```

We checked them.

After fixing the bugs:

```text
77 reported
77 correct
77 correct locations
```

That is positive-finding validation.

# What have we not checked?

The research-core profile contains eight rules:

```text
1. complex-expression
2. long-statement
3. incomplete-task
4. unstructured-module
5. empty-abstraction
6. excessive-nesting
7. missing-abstraction
8. broken-role-dependency
```

Nova produced findings for only two rules:

```text
complex-expression = 38
long-statement = 39
```

It produced zero findings for the other six:

```text
incomplete-task = 0
unstructured-module = 0
empty-abstraction = 0
excessive-nesting = 0
missing-abstraction = 0
broken-role-dependency = 0
```

But zero findings can mean two different things:

```text
Possibility A:
Nova genuinely has none of these smells.

Possibility B:
Some smells exist, but AnsibleGuard missed them.
```

We need to discover which possibility is true.

# What will we do exactly?

## Step 1: examine files AnsibleGuard called clean

We use the same frozen Nova project:

```text
Project:
openstack/openstack-ansible-os_nova

Commit:
e06c7bceef3f7c365828116b7aadea6fc2d3e22b

Production files:
28
```

We do not download a different version.

## Step 2: check each rule manually

For `complex-expression`, we ask:

```text
Is there a complicated Jinja or when expression
that AnsibleGuard did not report?
```

For `long-statement`, we ask:

```text
Is there a code line longer than 120 characters
that AnsibleGuard did not report?
```

For `incomplete-task`, we ask:

```text
Is there unfinished task evidence that was not reported?
```

For `empty-abstraction`, we ask:

```text
Is there an empty task block, handler or other abstraction
that was not reported?
```

For `excessive-nesting`, we ask:

```text
Is there deeply nested block/rescue/always code
that was not reported?
```

For `missing-abstraction`, we ask:

```text
Is there a very large group of tasks that should be divided,
but AnsibleGuard did not report it?
```

For `unstructured-module`, we ask:

```text
Is a role missing an expected structure,
but AnsibleGuard did not report it?
```

For `broken-role-dependency`, we ask:

```text
Is there a missing or circular role dependency
that AnsibleGuard did not report?
```

## Step 3: record every checked example

We will create another CSV, for example:

```text
study/labels/nova_research_core_negative_labels.csv
```

It will contain information such as:

| Rule | File | Line | Reported? | Human decision |
|---|---|---:|---:|---|
| complex-expression | `tasks/main.yml` | 50 | no | correctly clean |
| excessive-nesting | `tasks/install.yml` | 90 | no | correctly clean |
| incomplete-task | `tasks/setup.yml` | 30 | no | smell was missed |

## Step 4: label the result

For each checked location:

```text
true_negative
```

means:

> AnsibleGuard reported nothing, and the human agrees that there is no smell.

```text
false_negative
```

means:

> AnsibleGuard reported nothing, but the human found a smell.

```text
uncertain
```

means:

> We cannot confidently decide.

## Step 5: fix missed smells

If we discover a false negative:

1. understand why the detector missed it;
2. fix the detector;
3. create an automated regression test;
4. run all tests;
5. rerun Nova;
6. save the new results.

# What result will this give us?

Positive validation answers:

> When AnsibleGuard reports a smell, is it correct?

Negative validation answers:

> When a smell exists, can AnsibleGuard find it?

Together, they tell us whether the detector is trustworthy.

The simplest summary is:

```text
Previous work:
Check the problems AnsibleGuard found.

Next work:
Check whether AnsibleGuard missed other problems.
```

We should do this on the same 28 Nova files before moving to the other four OpenStack projects.
